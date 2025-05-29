"""
SSH connection and node installation service
"""

import paramiko
import logging
import time
import random
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
                        key_file = paramiko.StringIO(ssh_key)
                        try:
                            private_key = paramiko.RSAKey.from_private_key(key_file)
                        except paramiko.ssh_exception.PasswordRequiredException:
                            return False, "SSH key requires a passphrase (not supported)"
                        except Exception as e:
                            return False, f"Invalid SSH key format: {str(e)}"
                        
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
            for command in INSTALL_COMMANDS:
                success, output = self._execute_command(ssh_client, command)
                if not success:
                    return False, f"Failed at command: {command}\nOutput: {output}"
                logger.info(f"Command executed: {command}")
            
            # Create docker-compose.yml
            success, output = self._execute_command(
                ssh_client,
                f'cat > ~/Marzban-node/docker-compose.yml << EOF\n{DOCKER_COMPOSE_CONTENT}\nEOF'
            )
            if not success:
                return False, f"Failed to create docker-compose.yml: {output}"
            
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
            cert_command = f'cat > /var/lib/marzban-node/ssl_client_cert.pem << EOF\n{certificate}\nEOF'
            success, output = self._execute_command(ssh_client, cert_command)
            if not success:
                return False, f"Failed to create certificate file: {output}"
            
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
                        timeout: int = 300) -> Tuple[bool, str]:
        """Execute command on remote server"""
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
            
            # Wait for command to complete
            exit_status = stdout.channel.recv_exit_status()
            
            # Get output
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
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
                key_file = paramiko.StringIO(ssh_key)
                private_key = paramiko.RSAKey.from_private_key(key_file)
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
