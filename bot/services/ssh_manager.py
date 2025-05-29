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
            
            # Execute installation commands
            for i, command in enumerate(INSTALL_COMMANDS, 1):
                logger.info(f"Executing step {i}/{len(INSTALL_COMMANDS)}: {command}")
                success, output = self._execute_command(ssh_client, command)
                if not success:
                    logger.error(f"Command failed: {command}\nOutput: {output}")
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
            
            # Wait a moment for the service to start
            time.sleep(5)
            
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
            
            if exit_status == 0:
                return True, output
            else:
                return False, error or output
        
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return False, str(e)
    
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
