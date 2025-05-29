"""
SSH connection and node installation service
"""

import paramiko
import logging
import time
import random
import io
from typing import Tuple, Optional
from bot.config.settings import (
    SSH_TIMEOUT, MAX_SSH_RETRIES, DOCKER_COMPOSE_CONTENT, 
    INSTALL_COMMANDS, DEFAULT_NODE_PORT, DEFAULT_API_PORT
)
from bot.services.marzban_api import MarzbanAPI

logger = logging.getLogger(__name__)

class SSHManager:
    def __init__(self):
        self.marzban_api = MarzbanAPI()
    
    def install_node(self, ssh_ip: str, ssh_port: int, ssh_username: str,
                     ssh_password: str = None, ssh_key: str = None,
                     panel_id: int = None, node_name: str = None,
                     node_port: int = None, api_port: int = None,
                     db=None) -> Tuple[bool, str]:
        """Install Marzban node on remote server"""
        
        ssh_client = None
        try:
            logger.info(f"Starting SSH connection to {ssh_ip}:{ssh_port}")
            
            # Test connection first
            test_success, test_msg = self.test_ssh_connection(
                ssh_ip, ssh_port, ssh_username, ssh_password, ssh_key
            )
            
            if not test_success:
                return False, f"SSH connection test failed: {test_msg}"
            
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to server with retry logic
            for attempt in range(MAX_SSH_RETRIES):
                try:
                    if ssh_key:
                        # Use SSH key authentication
                        key_file = io.StringIO(ssh_key)
                        try:
                            # Try different key types
                            private_key = None
                            key_types = [
                                paramiko.RSAKey,
                                paramiko.Ed25519Key,
                                paramiko.ECDSAKey,
                                paramiko.DSSKey
                            ]
                            
                            for key_type in key_types:
                                try:
                                    key_file.seek(0)
                                    private_key = key_type.from_private_key(key_file)
                                    break
                                except Exception:
                                    continue
                            
                            if not private_key:
                                return False, "❌ کلید SSH معتبر نیست! لطفاً کلید خصوصی (private key) معتبر وارد کنید"
                                
                        except paramiko.ssh_exception.PasswordRequiredException:
                            return False, "❌ کلید SSH نیاز به رمز عبور دارد (پشتیبانی نمی‌شود)"
                        except Exception as e:
                            return False, f"❌ فرمت کلید SSH اشتباه است: {str(e)}"
                        
                        ssh_client.connect(
                            hostname=ssh_ip,
                            port=ssh_port,
                            username=ssh_username,
                            pkey=private_key,
                            timeout=SSH_TIMEOUT,
                            look_for_keys=False,
                            allow_agent=False
                        )
                    else:
                        # Use password authentication
                        if not ssh_password:
                            return False, "SSH password is required"
                        
                        ssh_client.connect(
                            hostname=ssh_ip,
                            port=ssh_port,
                            username=ssh_username,
                            password=ssh_password,
                            timeout=SSH_TIMEOUT,
                            look_for_keys=False,
                            allow_agent=False
                        )
                    
                    logger.info(f"SSH connection successful on attempt {attempt + 1}")
                    break
                    
                except Exception as e:
                    logger.warning(f"SSH connection attempt {attempt + 1} failed: {e}")
                    if attempt == MAX_SSH_RETRIES - 1:
                        raise e
                    time.sleep(2)
            
            logger.info(f"SSH connection established to {ssh_ip}")
            
            # Execute installation commands with intelligent error handling
            for i, command in enumerate(INSTALL_COMMANDS, 1):
                logger.info(f"Executing step {i}/{len(INSTALL_COMMANDS)}: {command}")
                success, output = self._execute_command(ssh_client, command)
                
                if not success:
                    logger.warning(f"Command failed at step {i}: {command}")
                    logger.warning(f"Error output: {output}")
                    
                    # Try to fix common installation issues
                    if self._try_fix_installation_issues(ssh_client, output):
                        logger.info(f"Fixed installation issue, retrying step {i}")
                        # Retry the failed command
                        success, output = self._execute_command(ssh_client, command)
                        
                        if not success:
                            logger.error(f"Command still failed after fix attempt: {command}")
                            return False, f"Failed at step {i}: {command}\nOutput: {output}"
                    else:
                        logger.error(f"Could not fix installation issue: {command}")
                        return False, f"Failed at step {i}: {command}\nOutput: {output}"
                
                logger.info(f"Step {i} completed successfully: {command}")
                if output.strip():
                    logger.info(f"Command output: {output[:500]}...")  # Log first 500 chars
            
            # Create docker-compose.yml with correct content in Marzban-node directory
            docker_compose_command = f'''cd ~/Marzban-node && cat > docker-compose.yml << 'EOF'
{DOCKER_COMPOSE_CONTENT}
EOF'''
            
            logger.info("Creating docker-compose.yml file")
            success, output = self._execute_command(ssh_client, docker_compose_command)
            if not success:
                return False, f"Failed to create docker-compose.yml: {output}"
            
            # Verify file was created
            success, output = self._execute_command(ssh_client, 'ls -la ~/Marzban-node/docker-compose.yml')
            if not success:
                return False, f"docker-compose.yml file was not created properly"
            logger.info("docker-compose.yml created successfully")
            
            # Get panel information
            panel = db.get_panel(panel_id) if db and panel_id else None
            if not panel:
                return False, "Panel not found"
            
            # Get node settings (certificate)
            success, settings_data = self.marzban_api.get_node_settings(
                panel['url'],
                panel['access_token']
            )
            
            if not success or not settings_data:
                # Try to re-authenticate
                auth_success, token_data = self.marzban_api.authenticate(
                    panel['url'],
                    panel['username'],
                    panel['password']
                )
                
                if auth_success:
                    db.update_panel_token(panel_id, token_data.get('access_token'))
                    success, settings_data = self.marzban_api.get_node_settings(
                        panel['url'],
                        token_data.get('access_token')
                    )
            
            if not success or not settings_data:
                return False, "Failed to get node settings from panel"
            
            certificate = settings_data.get('certificate', '')
            
            # Create certificate file
            cert_command = f'''cat > /var/lib/marzban-node/ssl_client_cert.pem << 'EOF'
{certificate}
EOF'''
            
            logger.info("Creating SSL certificate file")
            success, output = self._execute_command(ssh_client, cert_command)
            if not success:
                return False, f"Failed to create certificate file: {output}"
            
            # Create node configuration
            node_config = f'''cat > /var/lib/marzban-node/.env << 'EOF'
SERVICE_PORT={node_port or DEFAULT_NODE_PORT}
XRAY_API_PORT={api_port or DEFAULT_API_PORT}
EOF'''
            
            logger.info("Creating node configuration file")
            success, output = self._execute_command(ssh_client, node_config)
            if not success:
                logger.warning(f"Failed to create node config: {output}")
            
            # Set proper permissions
            success, output = self._execute_command(ssh_client, 'chmod 600 /var/lib/marzban-node/ssl_client_cert.pem')
            if not success:
                logger.warning(f"Failed to set certificate permissions: {output}")
            
            # Verify certificate file was created
            success, output = self._execute_command(ssh_client, 'ls -la /var/lib/marzban-node/ssl_client_cert.pem')
            if not success:
                return False, f"Certificate file was not created properly"
            logger.info("SSL certificate file created successfully")
            
            # Start Marzban node
            success, output = self._execute_command(
                ssh_client,
                'cd ~/Marzban-node && docker compose up -d'
            )
            if not success:
                return False, f"Failed to start Marzban node: {output}"
            
            # Wait for the service to start
            logger.info("Waiting for Marzban node to start...")
            time.sleep(10)
            
            # Check if container is running
            success, output = self._execute_command(
                ssh_client,
                'cd ~/Marzban-node && docker compose ps'
            )
            if success:
                logger.info(f"Container status: {output}")
            
            # Check logs to ensure proper startup
            success, logs = self._execute_command(
                ssh_client,
                'cd ~/Marzban-node && docker compose logs --tail=20'
            )
            if success:
                logger.info(f"Container logs: {logs}")
            else:
                logger.warning("Could not retrieve container logs")
            
            # Add node to panel
            node_data = {
                'add_as_new_host': True,
                'address': ssh_ip,
                'api_port': api_port or DEFAULT_API_PORT,
                'name': node_name or f"node-{ssh_ip}",
                'port': node_port or DEFAULT_NODE_PORT,
                'usage_coefficient': 1
            }
            
            success, node_result = self.marzban_api.add_node(
                panel['url'],
                panel['access_token'],
                node_data
            )
            
            if success and node_result:
                # Save node to database
                if db:
                    db.add_node(
                        panel_id=panel_id,
                        node_id=node_result.get('id'),
                        name=node_result.get('name'),
                        address=node_result.get('address'),
                        port=node_result.get('port'),
                        api_port=node_result.get('api_port'),
                        usage_coefficient=node_result.get('usage_coefficient'),
                        xray_version=node_result.get('xray_version'),
                        status=node_result.get('status'),
                        message=node_result.get('message')
                    )
                
                logger.info(f"Node installed and added successfully: {node_name}")
                return True, "Node installed and configured successfully"
            else:
                return False, f"Node installed but failed to add to panel: {node_result}"
        
        except paramiko.AuthenticationException:
            logger.error("SSH authentication failed")
            return False, "SSH authentication failed"
        except paramiko.SSHException as e:
            logger.error(f"SSH connection error: {e}")
            return False, f"SSH connection error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during node installation: {e}")
            return False, f"Installation error: {str(e)}"
        finally:
            if ssh_client:
                ssh_client.close()
    
    def _execute_command(self, ssh_client: paramiko.SSHClient, command: str, 
                        timeout: int = 600) -> Tuple[bool, str]:
        """Execute command on remote server"""
        try:
            logger.info(f"Executing command: {command}")
            
            # Set timeout for the channel
            stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
            
            # Set timeout for the channel operations
            stdout.channel.settimeout(timeout)
            stderr.channel.settimeout(timeout)
            
            # Read output with timeout handling
            output_data = []
            error_data = []
            
            # Use select to handle non-blocking reads
            import select
            
            while True:
                # Check if command is still running
                if stdout.channel.exit_status_ready():
                    break
                
                # Read available data
                if stdout.channel.recv_ready():
                    chunk = stdout.read(4096).decode('utf-8', errors='ignore')
                    if chunk:
                        output_data.append(chunk)
                        logger.info(f"Command output chunk: {chunk[:200]}...")
                
                if stderr.channel.recv_stderr_ready():
                    chunk = stderr.read(4096).decode('utf-8', errors='ignore')
                    if chunk:
                        error_data.append(chunk)
                        logger.warning(f"Command error chunk: {chunk[:200]}...")
                
                # Small delay to prevent busy waiting
                import time
                time.sleep(0.1)
            
            # Get final exit status
            exit_status = stdout.channel.recv_exit_status()
            
            # Read any remaining data
            remaining_output = stdout.read().decode('utf-8', errors='ignore')
            remaining_error = stderr.read().decode('utf-8', errors='ignore')
            
            if remaining_output:
                output_data.append(remaining_output)
            if remaining_error:
                error_data.append(remaining_error)
            
            output = ''.join(output_data)
            error = ''.join(error_data)
            
            logger.info(f"Command completed with exit status: {exit_status}")
            
            # Special handling for certain commands that can have non-zero exit but are still successful
            if self._is_command_success(command, exit_status, output, error):
                return True, output or error
            elif exit_status == 0:
                return True, output
            else:
                return False, error or output
        
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return False, str(e)
    
    def _is_command_success(self, command: str, exit_status: int, output: str, error: str) -> bool:
        """Check if command is considered successful despite non-zero exit status"""
        # Commands that end with "|| true" should always be considered successful
        if command.strip().endswith("|| true"):
            logger.info(f"Command with '|| true' completed with status {exit_status} - treating as success")
            return True
        
        # pkill commands are successful if they don't find processes to kill
        if "pkill" in command and exit_status == 1:
            logger.info(f"pkill command found no processes to kill - treating as success")
            return True
        
        # Commands that are expected to sometimes fail gracefully
        graceful_commands = [
            "rm -f",  # File removal that might not exist
            "killall",  # Process killing that might not find processes
            "fuser",  # File usage check
        ]
        
        for graceful_cmd in graceful_commands:
            if graceful_cmd in command and exit_status in [1, -1]:
                logger.info(f"Graceful command '{graceful_cmd}' completed with status {exit_status} - treating as success")
                return True
        
        return False
    
    def _try_fix_installation_issues(self, ssh_client: paramiko.SSHClient, error_output: str) -> bool:
        """Try to fix common installation issues automatically"""
        try:
            logger.info("Attempting to fix installation issues...")
            
            # Fix dpkg interruption issues
            if "dpkg was interrupted" in error_output or "dpkg --configure -a" in error_output:
                logger.info("Detected dpkg interruption, fixing...")
                
                # Kill any running dpkg processes
                self._execute_command(ssh_client, "pkill -f dpkg || true")
                time.sleep(2)
                
                # Remove lock files
                fix_commands = [
                    "rm -f /var/lib/dpkg/lock-frontend",
                    "rm -f /var/lib/dpkg/lock",
                    "rm -f /var/cache/apt/archives/lock",
                    "dpkg --configure -a",
                    "apt-get -f install"
                ]
                
                for cmd in fix_commands:
                    success, output = self._execute_command(ssh_client, cmd)
                    if success:
                        logger.info(f"Fix command successful: {cmd}")
                    else:
                        logger.warning(f"Fix command failed: {cmd} - {output}")
                
                return True
            
            # Fix apt lock issues
            elif "Could not get lock" in error_output or "Unable to lock" in error_output:
                logger.info("Detected apt lock issues, fixing...")
                
                # Wait for other package managers and remove locks
                fix_commands = [
                    "while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do echo 'Waiting...'; sleep 5; done",
                    "rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock",
                    "apt-get clean",
                    "apt-get update"
                ]
                
                for cmd in fix_commands:
                    success, output = self._execute_command(ssh_client, cmd)
                    if success:
                        logger.info(f"Lock fix successful: {cmd}")
                    else:
                        logger.warning(f"Lock fix failed: {cmd} - {output}")
                
                return True
            
            # Fix broken packages
            elif "broken packages" in error_output.lower() or "unmet dependencies" in error_output.lower():
                logger.info("Detected broken packages, fixing...")
                
                fix_commands = [
                    "apt-get clean",
                    "apt-get autoclean",
                    "apt-get -f install",
                    "dpkg --configure -a",
                    "apt-get update"
                ]
                
                for cmd in fix_commands:
                    success, output = self._execute_command(ssh_client, cmd)
                    if success:
                        logger.info(f"Package fix successful: {cmd}")
                    else:
                        logger.warning(f"Package fix failed: {cmd} - {output}")
                
                return True
            
            # Fix repository issues
            elif "repository" in error_output.lower() and ("not found" in error_output.lower() or "fail" in error_output.lower()):
                logger.info("Detected repository issues, fixing...")
                
                fix_commands = [
                    "apt-get clean",
                    "rm -rf /var/lib/apt/lists/*",
                    "apt-get update"
                ]
                
                for cmd in fix_commands:
                    success, output = self._execute_command(ssh_client, cmd)
                    if success:
                        logger.info(f"Repository fix successful: {cmd}")
                    else:
                        logger.warning(f"Repository fix failed: {cmd} - {output}")
                
                return True
            
            logger.info("No specific fix pattern matched")
            return False
            
        except Exception as e:
            logger.error(f"Error while trying to fix installation issues: {e}")
            return False

    def test_ssh_connection(self, ssh_ip: str, ssh_port: int, ssh_username: str,
                          ssh_password: str = None, ssh_key: str = None) -> Tuple[bool, str]:
        """Test SSH connection to server"""
        ssh_client = None
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if ssh_key:
                key_file = io.StringIO(ssh_key)
                private_key = None
                key_types = [
                    paramiko.RSAKey,
                    paramiko.Ed25519Key,
                    paramiko.ECDSAKey,
                    paramiko.DSSKey
                ]
                
                for key_type in key_types:
                    try:
                        key_file.seek(0)
                        private_key = key_type.from_private_key(key_file)
                        break
                    except Exception:
                        continue
                
                if not private_key:
                    return False, "❌ کلید SSH معتبر نیست!"
                ssh_client.connect(
                    hostname=ssh_ip,
                    port=ssh_port,
                    username=ssh_username,
                    pkey=private_key,
                    timeout=SSH_TIMEOUT
                )
            else:
                ssh_client.connect(
                    hostname=ssh_ip,
                    port=ssh_port,
                    username=ssh_username,
                    password=ssh_password,
                    timeout=SSH_TIMEOUT
                )
            
            # Test with simple command
            success, output = self._execute_command(ssh_client, 'echo "Connection test successful"')
            
            if success:
                return True, "SSH connection successful"
            else:
                return False, f"Command execution failed: {output}"
        
        except paramiko.AuthenticationException:
            return False, "SSH authentication failed"
        except paramiko.SSHException as e:
            return False, f"SSH connection error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
        finally:
            if ssh_client:
                ssh_client.close()
