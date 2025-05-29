
"""
Database management for the bot
"""

import sqlite3
import logging
import threading
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'bot_database.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT DEFAULT 'en',
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Panels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS panels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    panel_type TEXT DEFAULT 'marzban',
                    access_token TEXT,
                    token_expires TIMESTAMP,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (added_by) REFERENCES users (user_id)
                )
            ''')
            
            # Nodes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER,
                    node_id INTEGER,
                    name TEXT,
                    address TEXT,
                    port INTEGER,
                    api_port INTEGER,
                    usage_coefficient REAL DEFAULT 1.0,
                    xray_version TEXT,
                    status TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (panel_id) REFERENCES panels (id)
                )
            ''')
            
            # SSH servers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ssh_servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    port INTEGER DEFAULT 22,
                    username TEXT NOT NULL,
                    auth_method TEXT DEFAULT 'password',
                    password TEXT,
                    ssh_key TEXT,
                    status TEXT DEFAULT 'pending',
                    node_id INTEGER,
                    added_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (node_id) REFERENCES nodes (id),
                    FOREIGN KEY (added_by) REFERENCES users (user_id)
                )
            ''')
            
            # Bot statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE,
                    total_users INTEGER DEFAULT 0,
                    active_users INTEGER DEFAULT 0,
                    panels_added INTEGER DEFAULT 0,
                    nodes_installed INTEGER DEFAULT 0,
                    commands_executed INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, language: str = 'en') -> bool:
        """Add or update user"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, language, last_active)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name, language))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                
                conn.close()
                
                if result:
                    return {
                        'user_id': result[0],
                        'username': result[1],
                        'first_name': result[2],
                        'last_name': result[3],
                        'language': result[4],
                        'is_admin': bool(result[5]),
                        'created_at': result[6],
                        'last_active': result[7]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_language(self, user_id: int, language: str) -> bool:
        """Update user language"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET language = ?, last_active = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (language, user_id))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    def add_panel(self, name: str, url: str, username: str, password: str, 
                  panel_type: str = 'marzban', added_by: int = None) -> Optional[int]:
        """Add new panel"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO panels (name, url, username, password, panel_type, added_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, url, username, password, panel_type, added_by))
                
                panel_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return panel_id
        except Exception as e:
            logger.error(f"Error adding panel: {e}")
            return None
    
    def get_panels(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Get all panels or panels by user"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if user_id:
                    cursor.execute('SELECT * FROM panels WHERE added_by = ?', (user_id,))
                else:
                    cursor.execute('SELECT * FROM panels')
                
                results = cursor.fetchall()
                conn.close()
                
                panels = []
                for result in results:
                    panels.append({
                        'id': result[0],
                        'name': result[1],
                        'url': result[2],
                        'username': result[3],
                        'password': result[4],
                        'panel_type': result[5],
                        'access_token': result[6],
                        'token_expires': result[7],
                        'added_by': result[8],
                        'created_at': result[9]
                    })
                return panels
        except Exception as e:
            logger.error(f"Error getting panels: {e}")
            return []
    
    def get_panel(self, panel_id: int) -> Optional[Dict[str, Any]]:
        """Get panel by ID"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM panels WHERE id = ?', (panel_id,))
                result = cursor.fetchone()
                
                conn.close()
                
                if result:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'url': result[2],
                        'username': result[3],
                        'password': result[4],
                        'panel_type': result[5],
                        'access_token': result[6],
                        'token_expires': result[7],
                        'added_by': result[8],
                        'created_at': result[9]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting panel: {e}")
            return None
    
    def update_panel_token(self, panel_id: int, access_token: str, expires_at: str = None) -> bool:
        """Update panel access token"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE panels SET access_token = ?, token_expires = ?
                    WHERE id = ?
                ''', (access_token, expires_at, panel_id))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"Error updating panel token: {e}")
            return False
    
    def add_node(self, panel_id: int, node_id: int, name: str, address: str, 
                 port: int, api_port: int, usage_coefficient: float = 1.0,
                 xray_version: str = None, status: str = None, message: str = None) -> Optional[int]:
        """Add new node"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO nodes 
                    (panel_id, node_id, name, address, port, api_port, usage_coefficient, 
                     xray_version, status, message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (panel_id, node_id, name, address, port, api_port, usage_coefficient,
                      xray_version, status, message))
                
                db_node_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return db_node_id
        except Exception as e:
            logger.error(f"Error adding node: {e}")
            return None
    
    def get_nodes(self, panel_id: int = None) -> List[Dict[str, Any]]:
        """Get nodes by panel"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                if panel_id:
                    cursor.execute('SELECT * FROM nodes WHERE panel_id = ?', (panel_id,))
                else:
                    cursor.execute('SELECT * FROM nodes')
                
                results = cursor.fetchall()
                conn.close()
                
                nodes = []
                for result in results:
                    nodes.append({
                        'id': result[0],
                        'panel_id': result[1],
                        'node_id': result[2],
                        'name': result[3],
                        'address': result[4],
                        'port': result[5],
                        'api_port': result[6],
                        'usage_coefficient': result[7],
                        'xray_version': result[8],
                        'status': result[9],
                        'message': result[10],
                        'created_at': result[11],
                        'updated_at': result[12]
                    })
                return nodes
        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            return []
    
    def update_node(self, db_node_id: int, **kwargs) -> bool:
        """Update node information"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Build update query dynamically
                fields = []
                values = []
                for key, value in kwargs.items():
                    if key in ['name', 'address', 'port', 'api_port', 'usage_coefficient',
                              'xray_version', 'status', 'message']:
                        fields.append(f"{key} = ?")
                        values.append(value)
                
                if fields:
                    fields.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(db_node_id)
                    
                    query = f"UPDATE nodes SET {', '.join(fields)} WHERE id = ?"
                    cursor.execute(query, values)
                    
                    conn.commit()
                
                conn.close()
                return True
        except Exception as e:
            logger.error(f"Error updating node: {e}")
            return False
    
    def delete_node(self, db_node_id: int) -> bool:
        """Delete node"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM nodes WHERE id = ?', (db_node_id,))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            return False
    
    def create_backup(self) -> str:
        """Create database backup"""
        try:
            backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            with self.lock:
                # Copy database file
                import shutil
                shutil.copy2(self.db_path, backup_path)
            
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Count users
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                # Count panels
                cursor.execute('SELECT COUNT(*) FROM panels')
                total_panels = cursor.fetchone()[0]
                
                # Count nodes
                cursor.execute('SELECT COUNT(*) FROM nodes')
                total_nodes = cursor.fetchone()[0]
                
                # Count active users (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE last_active > datetime('now', '-1 day')
                ''')
                active_users = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'total_users': total_users,
                    'total_panels': total_panels,
                    'total_nodes': total_nodes,
                    'active_users': active_users
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
