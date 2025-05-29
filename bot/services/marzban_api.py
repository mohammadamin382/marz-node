
"""
Marzban panel API service
"""

import requests
import logging
from typing import Tuple, Dict, Any, List, Optional
from bot.config.settings import API_TIMEOUT, MAX_API_RETRIES

logger = logging.getLogger(__name__)

class MarzbanAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = API_TIMEOUT
    
    def verify_token(self, panel_url: str, access_token: str) -> bool:
        """Verify if token is still valid"""
        try:
            url = f"{panel_url.rstrip('/')}/api/admin"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, headers=headers)
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False
    
    def authenticate(self, panel_url: str, username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authenticate with Marzban panel"""
        try:
            url = f"{panel_url.rstrip('/')}/api/admin/token"
            
            data = {
                'username': username,
                'password': password
            }
            
            response = self.session.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                return True, token_data
            elif response.status_code == 422:
                # Validation error
                error_data = response.json()
                logger.error(f"Authentication validation error: {error_data}")
                return False, error_data
            else:
                logger.error(f"Authentication failed with status {response.status_code}")
                return False, None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during authentication: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return False, None
    
    def get_nodes(self, panel_url: str, access_token: str) -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
        """Get list of nodes from panel"""
        try:
            url = f"{panel_url.rstrip('/')}/api/nodes"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                nodes_data = response.json()
                return True, nodes_data
            elif response.status_code == 401:
                # Not authenticated
                error_data = response.json()
                if "Not authenticated" in str(error_data):
                    return False, "not_authenticated"
                return False, error_data
            elif response.status_code == 403:
                # Not allowed (not sudo)
                error_data = response.json()
                if "not allowed" in str(error_data):
                    return False, "not_sudo"
                return False, error_data
            else:
                logger.error(f"Get nodes failed with status {response.status_code}")
                return False, None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting nodes: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error getting nodes: {e}")
            return False, None
    
    def get_node_info(self, panel_url: str, access_token: str, node_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Get information about specific node"""
        try:
            url = f"{panel_url.rstrip('/')}/api/node/{node_id}"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                node_data = response.json()
                return True, node_data
            elif response.status_code == 401:
                return False, "not_authenticated"
            elif response.status_code == 403:
                return False, "not_sudo"
            elif response.status_code == 404:
                return False, "node_not_found"
            else:
                logger.error(f"Get node info failed with status {response.status_code}")
                return False, None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting node info: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error getting node info: {e}")
            return False, None
    
    def reconnect_node(self, panel_url: str, access_token: str, node_id: int) -> Tuple[bool, Optional[str]]:
        """Reconnect node"""
        try:
            url = f"{panel_url.rstrip('/')}/api/node/{node_id}/reconnect"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json() if response.content else "Success"
                return True, result
            elif response.status_code == 401:
                return False, "not_authenticated"
            elif response.status_code == 403:
                return False, "not_sudo"
            else:
                logger.error(f"Reconnect node failed with status {response.status_code}")
                return False, None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error reconnecting node: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error reconnecting node: {e}")
            return False, None
    
    def delete_node(self, panel_url: str, access_token: str, node_id: int) -> Tuple[bool, Optional[str]]:
        """Delete node"""
        try:
            url = f"{panel_url.rstrip('/')}/api/node/{node_id}"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.delete(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json() if response.content else "Success"
                return True, result
            elif response.status_code == 401:
                return False, "not_authenticated"
            elif response.status_code == 403:
                return False, "not_sudo"
            else:
                logger.error(f"Delete node failed with status {response.status_code}")
                return False, None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error deleting node: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error deleting node: {e}")
            return False, None
    
    def get_node_settings(self, panel_url: str, access_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Get node settings including certificate"""
        try:
            url = f"{panel_url.rstrip('/')}/api/node/settings"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                settings_data = response.json()
                return True, settings_data
            else:
                logger.error(f"Get node settings failed with status {response.status_code}")
                return False, None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting node settings: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error getting node settings: {e}")
            return False, None
    
    def add_node(self, panel_url: str, access_token: str, node_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Add new node to panel"""
        try:
            url = f"{panel_url.rstrip('/')}/api/node"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(url, json=node_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                result_data = response.json()
                return True, result_data
            elif response.status_code == 401:
                logger.error("Authentication failed - Invalid or expired token")
                return False, "not_authenticated"
            elif response.status_code == 403:
                logger.error("Access forbidden - User doesn't have sudo permissions")
                return False, "not_sudo"
            elif response.status_code == 422:
                # Validation error
                error_data = response.json()
                logger.error(f"Validation error: {error_data}")
                return False, error_data
            else:
                logger.error(f"Add node failed with status {response.status_code}: {response.text}")
                return False, response.text
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error adding node: {e}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error adding node: {e}")
            return False, f"Unexpected error: {str(e)}"
