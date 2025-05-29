"""Node management handler"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.db_manager import DatabaseManager
from bot.texts.bot_texts import get_text
from bot.services.marzban_api import MarzbanAPI
from bot.services.ssh_manager import SSHManager
from bot.utils.decorators import admin_only
import logging
import random
import string
import threading
import time
import os
import sqlite3
import shutil

logger = logging.getLogger(__name__)

class NodeHandler:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db
        self.marzban_api = MarzbanAPI()
        self.ssh_manager = SSHManager()

    @admin_only
    def handle_manage_nodes_menu(self, call):
        """Show node management menu"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'

        # Get user's panels
        panels = self.db.get_panels(call.from_user.id)

        if not panels:
            self.bot.edit_message_text(
                get_text('no_panels', lang),
                call.message.chat.id,
                call.message.message_id
            )
            return

        # Show panel selection
        keyboard = InlineKeyboardMarkup()
        for panel in panels:
            keyboard.row(InlineKeyboardButton(
                f"🚀 {panel['name']}",
                callback_data=f'node_select_panel_{panel["id"]}'
            ))

        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data='node_back_main'
        ))

        self.bot.edit_message_text(
            get_text('select_panel', lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    def handle_callback(self, call):
        """Handle node-related callbacks"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'

        if call.data.startswith('node_select_panel_'):
            panel_id = int(call.data.split('_')[3])
            self._show_node_management_options(call, panel_id, lang)

        elif call.data.startswith('node_list_'):
            panel_id = int(call.data.split('_')[2])
            self._show_nodes_list(call, panel_id, lang)

        elif call.data.startswith('node_add_'):
            panel_id = int(call.data.split('_')[2])
            self._show_add_node_options(call, panel_id, lang)

        elif call.data.startswith('node_info_'):
            parts = call.data.split('_')
            panel_id = int(parts[2])
            node_id = int(parts[3])
            self._show_node_info(call, panel_id, node_id, lang)

        elif call.data.startswith('node_reconnect_'):
            parts = call.data.split('_')
            panel_id = int(parts[2])
            node_id = int(parts[3])
            self._reconnect_node(call, panel_id, node_id, lang)

        elif call.data.startswith('node_delete_'):
            parts = call.data.split('_')
            panel_id = int(parts[2])
            node_id = int(parts[3])
            self._delete_node(call, panel_id, node_id, lang)

        elif call.data.startswith('node_update_'):
            parts = call.data.split('_')
            panel_id = int(parts[2])
            node_id = int(parts[3])
            self._update_node_info(call, panel_id, node_id, lang)

        elif call.data.startswith('node_install_single_'):
            panel_id = int(call.data.split('_')[3])
            self._start_single_install(call, panel_id, lang)

        elif call.data.startswith('node_install_bulk_'):
            panel_id = int(call.data.split('_')[3])
            self._start_bulk_install(call, panel_id, lang)

        elif call.data.startswith('node_servers_'):
            panel_id = int(call.data.split('_')[2])
            self._show_node_servers(call, panel_id, lang)

        elif call.data.startswith('server_info_'):
            server_id = call.data.split('_')[2]
            self._show_server_info(call, server_id, lang)

        elif call.data == 'backup_restore':
            self._show_backup_restore_menu(call, lang)

        elif call.data == 'upload_backup':
            self._start_backup_upload(call, lang)

        elif call.data == 'node_back_main':
            from bot.handlers.start_handler import StartHandler
            start_handler = StartHandler(self.bot, self.db)
            start_handler.show_main_menu(call.message, lang)

    def _show_node_management_options(self, call, panel_id, lang):
        """Show node management options for selected panel"""
        keyboard = InlineKeyboardMarkup()

        keyboard.row(InlineKeyboardButton(
            get_text('list_nodes', lang),
            callback_data=f'node_list_{panel_id}'
        ))

        keyboard.row(InlineKeyboardButton(
            get_text('add_new_node', lang),
            callback_data=f'node_add_{panel_id}'
        ))

        keyboard.row(InlineKeyboardButton(
            get_text('node_servers', lang),
            callback_data=f'node_servers_{panel_id}'
        ))

        keyboard.row(InlineKeyboardButton(
            get_text('backup_restore', lang),
            callback_data='backup_restore'
        ))

        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data='node_back_main'
        ))

        self.bot.edit_message_text(
            get_text('node_management', lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    def _show_nodes_list(self, call, panel_id, lang):
        """Show list of nodes for panel"""
        try:
            panel = self.db.get_panel(panel_id)
            if not panel:
                self.bot.answer_callback_query(call.id, get_text('error_occurred', lang))
                return

            # Get nodes from API
            success, nodes_data = self.marzban_api.get_nodes(
                panel['url'],
                panel['access_token']
            )

            if not success:
                # Try to re-authenticate
                auth_success, token_data = self.marzban_api.authenticate(
                    panel['url'],
                    panel['username'],
                    panel['password']
                )

                if auth_success:
                    self.db.update_panel_token(
                        panel_id,
                        token_data.get('access_token')
                    )

                    success, nodes_data = self.marzban_api.get_nodes(
                        panel['url'],
                        token_data.get('access_token')
                    )

            if success and nodes_data:
                keyboard = InlineKeyboardMarkup()

                for node in nodes_data:
                    status_emoji = "🟢" if node.get('status') == 'connected' else "🔴"
                    keyboard.row(InlineKeyboardButton(
                        f"{status_emoji} {node.get('name', 'Unnamed')}",
                        callback_data=f'node_info_{panel_id}_{node.get("id")}'
                    ))

                keyboard.row(InlineKeyboardButton(
                    get_text('back', lang),
                    callback_data=f'node_select_panel_{panel_id}'
                ))

                text = get_text('nodes_list', lang)
            else:
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton(
                    get_text('back', lang),
                    callback_data=f'node_select_panel_{panel_id}'
                ))
                text = get_text('no_nodes', lang)

            self.bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"Error showing nodes list: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e))
            )

    def _show_node_info(self, call, panel_id, node_id, lang):
        """Show detailed node information"""
        try:
            panel = self.db.get_panel(panel_id)
            if not panel:
                return

            # Get node info from API
            success, node_data = self.marzban_api.get_node_info(
                panel['url'],
                panel['access_token'],
                node_id
            )

            if success and node_data:
                # Format node information (truncated for Telegram limits)
                info_text = f"{get_text('node_info', lang)}\n\n"
                info_text += f"🏷️ Name: {node_data.get('name', 'N/A')}\n"
                info_text += f"🌐 Address: {node_data.get('address', 'N/A')}\n"
                info_text += f"🔌 Port: {node_data.get('port', 'N/A')}\n"
                info_text += f"🔧 API Port: {node_data.get('api_port', 'N/A')}\n"
                info_text += f"📊 Usage Coefficient: {node_data.get('usage_coefficient', 'N/A')}\n"
                
                xray_version = node_data.get('xray_version', 'N/A')
                if xray_version and len(str(xray_version)) > 20:
                    xray_version = str(xray_version)[:20] + "..."
                info_text += f"🔗 Xray Version: {xray_version}\n"

                status = node_data.get('status', 'unknown')
                status_emoji = "🟢" if status == 'connected' else "🔴"
                info_text += f"{status_emoji} Status: {status}\n"

                # Truncate message if too long
                message = node_data.get('message', '')
                if message:
                    if len(message) > 100:
                        message = message[:100] + "..."
                    info_text += f"💬 Message: {message}\n"

                keyboard = InlineKeyboardMarkup()
                keyboard.row(
                    InlineKeyboardButton(
                        "🔄 " + get_text('reconnect_node', lang)[:10],
                        callback_data=f'node_reconnect_{panel_id}_{node_id}'
                    ),
                    InlineKeyboardButton(
                        "🗑️ " + get_text('delete_node', lang)[:10],
                        callback_data=f'node_delete_{panel_id}_{node_id}'
                    )
                )
                keyboard.row(InlineKeyboardButton(
                    get_text('update_node', lang),
                    callback_data=f'node_update_{panel_id}_{node_id}'
                ))
                keyboard.row(InlineKeyboardButton(
                    get_text('back', lang),
                    callback_data=f'node_list_{panel_id}'
                ))

                self.bot.edit_message_text(
                    info_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard
                )
            else:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('node_not_found', lang)
                )

        except Exception as e:
            logger.error(f"Error showing node info: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e))
            )

    def _show_add_node_options(self, call, panel_id, lang):
        """Show add node options"""
        keyboard = InlineKeyboardMarkup()

        keyboard.row(InlineKeyboardButton(
            get_text('single_install', lang),
            callback_data=f'node_install_single_{panel_id}'
        ))

        keyboard.row(InlineKeyboardButton(
            get_text('bulk_install', lang),
            callback_data=f'node_install_bulk_{panel_id}'
        ))

        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data=f'node_select_panel_{panel_id}'
        ))

        self.bot.edit_message_text(
            get_text('install_type', lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    def _start_single_install(self, call, panel_id, lang):
        """Start single node installation process"""
        user_id = call.from_user.id
        session_data = {
            'step': 'ssh_ip',
            'panel_id': panel_id,
            'data': {},
            'handler': self._handle_install_input
        }

        self.bot.active_sessions = getattr(self.bot, 'active_sessions', {})
        self.bot.active_sessions[user_id] = session_data

        self.bot.edit_message_text(
            get_text('enter_ssh_ip', lang),
            call.message.chat.id,
            call.message.message_id
        )

    def _handle_install_input(self, message, session):
        """Handle node installation input"""
        user = self.db.get_user(message.from_user.id)
        lang = user['language'] if user else 'en'
        user_id = message.from_user.id

        try:
            if session['step'] == 'ssh_ip':
                session['data']['ssh_ip'] = message.text.strip()
                session['step'] = 'ssh_port'
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_ssh_port', lang)
                )

            elif session['step'] == 'ssh_port':
                try:
                    port = int(message.text.strip())
                    session['data']['ssh_port'] = port
                except ValueError:
                    session['data']['ssh_port'] = 22

                session['step'] = 'ssh_username'
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_ssh_username', lang)
                )

            elif session['step'] == 'ssh_username':
                session['data']['ssh_username'] = message.text.strip()
                session['step'] = 'auth_method'

                keyboard = InlineKeyboardMarkup()
                keyboard.row(
                    InlineKeyboardButton(
                        get_text('password_auth', lang),
                        callback_data='install_auth_password'
                    ),
                    InlineKeyboardButton(
                        get_text('ssh_key_auth', lang),
                        callback_data='install_auth_key'
                    )
                )

                self.bot.send_message(
                    message.chat.id,
                    get_text('auth_method', lang),
                    reply_markup=keyboard
                )
                return  # Don't continue to next step yet

            elif session['step'] == 'ssh_password':
                session['data']['ssh_password'] = message.text.strip()
                self._continue_to_node_name(message, session, lang)

            elif session['step'] == 'ssh_key':
                try:
                    if message.document:
                        # Handle file upload
                        file_info = self.bot.get_file(message.document.file_id)
                        file_content = self.bot.download_file(file_info.file_path)
                        ssh_key_content = file_content.decode('utf-8').strip()
                    else:
                        # Handle text input
                        ssh_key_content = message.text.strip()
                    
                    # Validate SSH key format
                    if not ssh_key_content.startswith('-----BEGIN'):
                        self.bot.send_message(
                            message.chat.id,
                            get_text('invalid_ssh_key_format', lang)
                        )
                        return
                    
                    session['data']['ssh_key'] = ssh_key_content
                    
                    # Test the SSH key
                    self.bot.send_message(
                        message.chat.id,
                        get_text('testing_ssh_connection', lang)
                    )
                    
                    test_success, test_msg = self.ssh_manager.test_ssh_connection(
                        session['data']['ssh_ip'],
                        session['data']['ssh_port'],
                        session['data']['ssh_username'],
                        ssh_key=ssh_key_content
                    )
                    
                    if not test_success:
                        self.bot.send_message(
                            message.chat.id,
                            get_text('ssh_test_failed', lang, error=test_msg)
                        )
                        return
                    
                    self.bot.send_message(
                        message.chat.id,
                        get_text('ssh_test_success', lang)
                    )
                    
                    self._continue_to_node_name(message, session, lang)
                    
                except Exception as e:
                    logger.error(f"Error handling SSH key: {e}")
                    self.bot.send_message(
                        message.chat.id,
                        get_text('error_occurred', lang, error=str(e))
                    )

            elif session['step'] == 'node_name':
                if message.text.strip().lower() in ['random', 'رندوم', 'случайно']:
                    session['data']['node_name'] = self._generate_random_name()
                else:
                    session['data']['node_name'] = message.text.strip()

                # Set fixed ports
                from bot.config.settings import FIXED_NODE_PORT, FIXED_API_PORT
                session['data']['node_port'] = FIXED_NODE_PORT
                session['data']['api_port'] = FIXED_API_PORT

                # Start installation
                self._start_node_installation(message, session, lang, user_id)

            elif session['step'] == 'backup_upload':
                self._handle_backup_upload(message, session, lang, user_id)

            elif session['step'] == 'backup_merge_choice':
                choice = message.text.strip().lower()
                if choice in ['merge', 'ادغام', 'объединить']:
                    session['merge_type'] = 'merge'
                else:
                    session['merge_type'] = 'replace'
                self._process_backup_restore(message, session, lang, user_id)

        except Exception as e:
            logger.error(f"Error handling install input: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('error_occurred', lang, error=str(e))
            )

            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]

    def _continue_to_node_name(self, message, session, lang):
        """Continue to node name configuration"""
        session['step'] = 'node_name'
        
        # Set fixed ports automatically
        from bot.config.settings import FIXED_NODE_PORT, FIXED_API_PORT
        session['data']['node_port'] = FIXED_NODE_PORT
        session['data']['api_port'] = FIXED_API_PORT

        self.bot.send_message(
            message.chat.id,
            get_text('enter_node_name', lang)
        )

    def _generate_random_name(self):
        """Generate random node name"""
        return f"node-{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

    def _start_node_installation(self, message, session, lang, user_id):
        """Start the actual node installation process with progress tracking"""
        try:
            # Send initial message with warning
            warning_msg = self.bot.send_message(
                message.chat.id,
                get_text('installation_warning', lang)
            )

            # Send progress message
            progress_msg = self.bot.send_message(
                message.chat.id,
                get_text('installing_node_progress', lang, progress=0)
            )

            # Create progress tracker in a separate thread
            progress_thread = threading.Thread(
                target=self._update_progress_tracker,
                args=(message.chat.id, progress_msg.message_id, lang)
            )
            progress_thread.daemon = True
            progress_thread.start()

            # Install node using SSH manager
            success, result = self.ssh_manager.install_node(
                ssh_ip=session['data']['ssh_ip'],
                ssh_port=session['data']['ssh_port'],
                ssh_username=session['data']['ssh_username'],
                ssh_password=session['data'].get('ssh_password'),
                ssh_key=session['data'].get('ssh_key'),
                panel_id=session['panel_id'],
                node_name=session['data']['node_name'],
                node_port=session['data']['node_port'],
                api_port=session['data']['api_port'],
                db=self.db,
                progress_callback=lambda p: setattr(self, '_current_progress', p)
            )

            # Stop progress tracker
            self._installation_complete = True

            if success:
                # Store server info for monitoring
                server_info = {
                    'ip': session['data']['ssh_ip'],
                    'port': session['data']['ssh_port'],
                    'username': session['data']['ssh_username'],
                    'password': session['data'].get('ssh_password'),
                    'ssh_key': session['data'].get('ssh_key'),
                    'node_name': session['data']['node_name'],
                    'panel_id': session['panel_id']
                }
                
                # Save server info to database
                self.db.add_server(server_info)

                self.bot.edit_message_text(
                    get_text('node_installed', lang),
                    message.chat.id,
                    progress_msg.message_id
                )
            else:
                self.bot.edit_message_text(
                    get_text('installation_failed', lang, error=result),
                    message.chat.id,
                    progress_msg.message_id
                )

        except Exception as e:
            logger.error(f"Error during node installation: {e}")
            self._installation_complete = True
            try:
                self.bot.edit_message_text(
                    get_text('installation_failed', lang, error=str(e)),
                    message.chat.id,
                    progress_msg.message_id
                )
            except:
                self.bot.send_message(
                    message.chat.id,
                    get_text('installation_failed', lang, error=str(e))
                )
        finally:
            # Clear session
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]

    def _update_progress_tracker(self, chat_id, message_id, lang):
        """Update installation progress"""
        self._current_progress = 0
        self._installation_complete = False
        
        while not self._installation_complete:
            try:
                progress = getattr(self, '_current_progress', 0)
                progress_text = get_text('installing_node_progress', lang, progress=progress)
                
                self.bot.edit_message_text(
                    progress_text,
                    chat_id,
                    message_id
                )
                
                time.sleep(2)
                
                # Auto increment if no manual progress
                if not hasattr(self, '_manual_progress'):
                    self._current_progress = min(self._current_progress + 5, 95)
                
            except Exception as e:
                logger.error(f"Error updating progress: {e}")
                break
            
            time.sleep(3)

    def _reconnect_node(self, call, panel_id, node_id, lang):
        """Reconnect node"""
        try:
            panel = self.db.get_panel(panel_id)
            if not panel:
                return

            success, result = self.marzban_api.reconnect_node(
                panel['url'],
                panel['access_token'],
                node_id
            )

            if success:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('node_reconnected', lang),
                    show_alert=True
                )
            else:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('error_occurred', lang, error=result),
                    show_alert=True
                )

        except Exception as e:
            logger.error(f"Error reconnecting node: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e)),
                show_alert=True
            )

    def _delete_node(self, call, panel_id, node_id, lang):
        """Delete node"""
        try:
            panel = self.db.get_panel(panel_id)
            if not panel:
                return

            success, result = self.marzban_api.delete_node(
                panel['url'],
                panel['access_token'],
                node_id
            )

            if success:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('node_deleted', lang),
                    show_alert=True
                )

                # Refresh nodes list
                self._show_nodes_list(call, panel_id, lang)
            else:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('error_occurred', lang, error=result),
                    show_alert=True
                )

        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e)),
                show_alert=True
            )

    def _update_node_info(self, call, panel_id, node_id, lang):
        """Update node information"""
        try:
            panel = self.db.get_panel(panel_id)
            if not panel:
                return

            success, node_data = self.marzban_api.get_node_info(
                panel['url'],
                panel['access_token'],
                node_id
            )

            if success:
                # Update local database
                db_nodes = self.db.get_nodes(panel_id)
                for db_node in db_nodes:
                    if db_node['node_id'] == node_id:
                        self.db.update_node(
                            db_node['id'],
                            name=node_data.get('name'),
                            address=node_data.get('address'),
                            port=node_data.get('port'),
                            api_port=node_data.get('api_port'),
                            usage_coefficient=node_data.get('usage_coefficient'),
                            xray_version=node_data.get('xray_version'),
                            status=node_data.get('status'),
                            message=node_data.get('message')
                        )
                        break

                self.bot.answer_callback_query(
                    call.id,
                    get_text('node_updated', lang),
                    show_alert=True
                )

                # Refresh node info
                self._show_node_info(call, panel_id, node_id, lang)
            else:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('error_occurred', lang),
                    show_alert=True
                )

        except Exception as e:
            logger.error(f"Error updating node info: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e)),
                show_alert=True
            )

        def _start_bulk_install(self, call, panel_id, lang):
        """Start bulk node installation process"""
        user_id = call.from_user.id
        session_data = {
            'step': 'bulk_servers',
            'panel_id': panel_id,
            'data': {},
            'handler': self._handle_bulk_install_input
        }

        self.bot.active_sessions = getattr(self.bot, 'active_sessions', {})
        self.bot.active_sessions[user_id] = session_data

        self.bot.edit_message_text(
            get_text('enter_bulk_servers', lang),
            call.message.chat.id,
            call.message.message_id
        )

    def _handle_bulk_install_input(self, message, session):
        """Handle bulk installation input"""
        user = self.db.get_user(message.from_user.id)
        lang = user['language'] if user else 'en'
        user_id = message.from_user.id

        try:
            if session['step'] == 'bulk_servers':
                # Parse server list from message
                servers = self._parse_bulk_servers(message.text)
                if not servers:
                    self.bot.send_message(
                        message.chat.id,
                        get_text('invalid_server_format', lang)
                    )
                    return

                session['data']['servers'] = servers
                session['step'] = 'bulk_auth_method'

                keyboard = InlineKeyboardMarkup()
                keyboard.row(
                    InlineKeyboardButton(
                        get_text('password_auth', lang),
                        callback_data='bulk_auth_password'
                    ),
                    InlineKeyboardButton(
                        get_text('ssh_key_auth', lang),
                        callback_data='bulk_auth_key'
                    )
                )

                self.bot.send_message(
                    message.chat.id,
                    get_text('auth_method', lang),
                    reply_markup=keyboard
                )

            elif session['step'] == 'bulk_auth_data':
                # Store auth data and start bulk installation
                auth_data = message.text.strip()
                if session.get('auth_type') == 'password':
                    session['data']['password'] = auth_data
                else:
                    session['data']['ssh_key'] = auth_data

                self._start_bulk_installation(message, session, lang, user_id)

        except Exception as e:
            logger.error(f"Error handling bulk install input: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('error_occurred', lang, error=str(e))
            )

    def _parse_bulk_servers(self, text):
        """Parse bulk server input"""
        servers = []
        lines = text.strip().split('\n')
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                ip = parts[0]
                username = parts[1]
                port = int(parts[2]) if len(parts) > 2 else 22
                
                servers.append({
                    'ip': ip,
                    'username': username,
                    'port': port
                })
        
        return servers

    def _start_bulk_installation(self, message, session, lang, user_id):
        """Start bulk installation process"""
        try:
            servers = session['data']['servers']
            total_servers = len(servers)
            
            self.bot.send_message(
                message.chat.id,
                get_text('bulk_installation_start', lang, count=total_servers)
            )

            for i, server in enumerate(servers, 1):
                try:
                    progress_msg = self.bot.send_message(
                        message.chat.id,
                        get_text('installing_server', lang, current=i, total=total_servers, ip=server['ip'])
                    )

                    from bot.config.settings import FIXED_NODE_PORT, FIXED_API_PORT
                    
                    success, result = self.ssh_manager.install_node(
                        ssh_ip=server['ip'],
                        ssh_port=server['port'],
                        ssh_username=server['username'],
                        ssh_password=session['data'].get('password'),
                        ssh_key=session['data'].get('ssh_key'),
                        panel_id=session['panel_id'],
                        node_name=f"node-{server['ip']}",
                        node_port=FIXED_NODE_PORT,
                        api_port=FIXED_API_PORT,
                        db=self.db
                    )

                    if success:
                        self.bot.edit_message_text(
                            get_text('server_installed_success', lang, ip=server['ip']),
                            message.chat.id,
                            progress_msg.message_id
                        )
                    else:
                        self.bot.edit_message_text(
                            get_text('server_installation_failed', lang, ip=server['ip'], error=result),
                            message.chat.id,
                            progress_msg.message_id
                        )

                except Exception as e:
                    logger.error(f"Error installing server {server['ip']}: {e}")
                    self.bot.send_message(
                        message.chat.id,
                        get_text('server_installation_failed', lang, ip=server['ip'], error=str(e))
                    )

            self.bot.send_message(
                message.chat.id,
                get_text('bulk_installation_complete', lang)
            )

        except Exception as e:
            logger.error(f"Error during bulk installation: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('installation_failed', lang, error=str(e))
            )
        finally:
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]

    def _show_node_servers(self, call, panel_id, lang):
        """Show node servers for monitoring"""
        try:
            servers = self.db.get_servers(panel_id)
            
            if not servers:
                self.bot.edit_message_text(
                    get_text('no_servers', lang),
                    call.message.chat.id,
                    call.message.message_id
                )
                return

            keyboard = InlineKeyboardMarkup()
            for server in servers:
                keyboard.row(InlineKeyboardButton(
                    f"🖥️ {server['ip']} ({server['node_name']})",
                    callback_data=f'server_info_{server["id"]}'
                ))

            keyboard.row(InlineKeyboardButton(
                get_text('back', lang),
                callback_data=f'node_select_panel_{panel_id}'
            ))

            self.bot.edit_message_text(
                get_text('servers_list', lang),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"Error showing servers: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e))
            )

    def _show_server_info(self, call, server_id, lang):
        """Show live server information"""
        try:
            server = self.db.get_server(server_id)
            if not server:
                self.bot.answer_callback_query(call.id, get_text('server_not_found', lang))
                return

            # Get live server stats
            stats = self._get_server_stats(server)
            
            info_text = f"{get_text('server_info', lang)}\n\n"
            info_text += f"🖥️ IP: {server['ip']}\n"
            info_text += f"🏷️ Name: {server['node_name']}\n"
            info_text += f"💾 RAM: {stats.get('ram_usage', 'N/A')}\n"
            info_text += f"💿 Disk: {stats.get('disk_usage', 'N/A')}\n"
            info_text += f"⚡ CPU: {stats.get('cpu_usage', 'N/A')}\n"
            info_text += f"🌐 Uptime: {stats.get('uptime', 'N/A')}\n"
            info_text += f"📊 Status: {stats.get('status', 'Unknown')}\n"

            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(
                "🔄 " + get_text('refresh', lang),
                callback_data=f'server_info_{server_id}'
            ))
            keyboard.row(InlineKeyboardButton(
                get_text('back', lang),
                callback_data=f'node_servers_{server["panel_id"]}'
            ))

            self.bot.edit_message_text(
                info_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"Error showing server info: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e))
            )

    def _get_server_stats(self, server):
        """Get live server statistics"""
        try:
            # Connect via SSH and get system stats
            import paramiko
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if server.get('ssh_key'):
                import io
                key_file = io.StringIO(server['ssh_key'])
                private_key = paramiko.RSAKey.from_private_key(key_file)
                ssh_client.connect(
                    hostname=server['ip'],
                    port=server['port'],
                    username=server['username'],
                    pkey=private_key,
                    timeout=10
                )
            else:
                ssh_client.connect(
                    hostname=server['ip'],
                    port=server['port'],
                    username=server['username'],
                    password=server.get('password'),
                    timeout=10
                )

            # Get system stats
            stats = {}
            
            # RAM usage
            stdin, stdout, stderr = ssh_client.exec_command("free -h | awk 'NR==2{printf \"%.2f%\", $3/$2*100}'")
            stats['ram_usage'] = stdout.read().decode().strip()
            
            # Disk usage
            stdin, stdout, stderr = ssh_client.exec_command("df -h / | awk 'NR==2{printf \"%s\", $5}'")
            stats['disk_usage'] = stdout.read().decode().strip()
            
            # CPU usage
            stdin, stdout, stderr = ssh_client.exec_command("top -bn1 | grep load | awk '{printf \"%.2f%%\", $(NF-2)}'")
            stats['cpu_usage'] = stdout.read().decode().strip()
            
            # Uptime
            stdin, stdout, stderr = ssh_client.exec_command("uptime -p")
            stats['uptime'] = stdout.read().decode().strip()
            
            stats['status'] = '🟢 Online'
            
            ssh_client.close()
            return stats

        except Exception as e:
            logger.error(f"Error getting server stats: {e}")
            return {
                'ram_usage': 'N/A',
                'disk_usage': 'N/A', 
                'cpu_usage': 'N/A',
                'uptime': 'N/A',
                'status': '🔴 Offline'
            }

    def _show_backup_restore_menu(self, call, lang):
        """Show backup and restore menu"""
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(
            get_text('upload_backup', lang),
            callback_data='upload_backup'
        ))
        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data='node_back_main'
        ))

        self.bot.edit_message_text(
            get_text('backup_restore_menu', lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )

    def _start_backup_upload(self, call, lang):
        """Start backup upload process"""
        user_id = call.from_user.id
        session_data = {
            'step': 'backup_upload',
            'handler': self._handle_install_input
        }

        self.bot.active_sessions = getattr(self.bot, 'active_sessions', {})
        self.bot.active_sessions[user_id] = session_data

        self.bot.edit_message_text(
            get_text('upload_backup_file', lang),
            call.message.chat.id,
            call.message.message_id
        )

    def _handle_backup_upload(self, message, session, lang, user_id):
        """Handle backup file upload"""
        try:
            if message.document and message.document.file_name.endswith('.db'):
                file_info = self.bot.get_file(message.document.file_id)
                file_content = self.bot.download_file(file_info.file_path)
                
                # Save backup file temporarily
                backup_path = f"/tmp/backup_{user_id}.db"
                with open(backup_path, 'wb') as f:
                    f.write(file_content)
                
                session['backup_path'] = backup_path
                session['step'] = 'backup_merge_choice'
                
                self.bot.send_message(
                    message.chat.id,
                    get_text('backup_merge_choice', lang)
                )
            else:
                self.bot.send_message(
                    message.chat.id,
                    get_text('invalid_backup_file', lang)
                )
        except Exception as e:
            logger.error(f"Error handling backup upload: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('error_occurred', lang, error=str(e))
            )

    def _process_backup_restore(self, message, session, lang, user_id):
        """Process backup restore based on user choice"""
        try:
            backup_path = session['backup_path']
            merge_type = session['merge_type']
            
            if merge_type == 'replace':
                # Replace current database
                current_db_path = self.db.db_path
                shutil.copy2(backup_path, current_db_path)
                self.bot.send_message(
                    message.chat.id,
                    get_text('backup_restored_replace', lang)
                )
            else:
                # Merge databases
                self._merge_databases(backup_path, self.db.db_path)
                self.bot.send_message(
                    message.chat.id,
                    get_text('backup_restored_merge', lang)
                )
            
            # Clean up
            os.remove(backup_path)
            
        except Exception as e:
            logger.error(f"Error processing backup restore: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('error_occurred', lang, error=str(e))
            )
        finally:
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]

    def _merge_databases(self, source_db, target_db):
        """Merge two databases"""
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        # Get all tables from source
        cursor = source_conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            try:
                # Copy data from source to target
                cursor = source_conn.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column info
                cursor = source_conn.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                placeholders = ','.join(['?' for _ in columns])
                target_conn.executemany(
                    f"INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})",
                    rows
                )
                
            except Exception as e:
                logger.warning(f"Error merging table {table_name}: {e}")
        
        target_conn.commit()
        source_conn.close()
        target_conn.close()
