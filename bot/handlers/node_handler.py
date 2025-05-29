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
                # Format node information
                info_text = f"{get_text('node_info', lang)}\n\n"
                info_text += f"🏷️ Name: {node_data.get('name', 'N/A')}\n"
                info_text += f"🌐 Address: {node_data.get('address', 'N/A')}\n"
                info_text += f"🔌 Port: {node_data.get('port', 'N/A')}\n"
                info_text += f"🔧 API Port: {node_data.get('api_port', 'N/A')}\n"
                info_text += f"📊 Usage Coefficient: {node_data.get('usage_coefficient', 'N/A')}\n"
                info_text += f"🔗 Xray Version: {node_data.get('xray_version', 'N/A')}\n"

                status = node_data.get('status', 'unknown')
                status_emoji = "🟢" if status == 'connected' else "🔴"
                info_text += f"{status_emoji} Status: {status}\n"

                if node_data.get('message'):
                    info_text += f"💬 Message: {node_data.get('message')}\n"

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
                self._continue_to_port_config(message, session, lang)

            elif session['step'] == 'ssh_key':
                if message.document:
                    # Handle file upload
                    file_info = self.bot.get_file(message.document.file_id)
                    file_content = self.bot.download_file(file_info.file_path)
                    session['data']['ssh_key'] = file_content.decode('utf-8')
                else:
                    # Handle text input
                    session['data']['ssh_key'] = message.text.strip()

                self._continue_to_port_config(message, session, lang)

            elif session['step'] == 'node_port':
                try:
                    port = int(message.text.strip())
                    session['data']['node_port'] = port
                except ValueError:
                    session['data']['node_port'] = random.randint(60000, 65000)

                session['step'] = 'api_port'
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_api_port', lang)
                )

            elif session['step'] == 'api_port':
                try:
                    port = int(message.text.strip())
                    session['data']['api_port'] = port
                except ValueError:
                    session['data']['api_port'] = random.randint(60000, 65000)

                session['step'] = 'node_name'
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_node_name', lang)
                )

            elif session['step'] == 'node_name':
                if message.text.strip().lower() in ['random', 'رندوم', 'случайно']:
                    session['data']['node_name'] = self._generate_random_name()
                else:
                    session['data']['node_name'] = message.text.strip()

                # Start installation
                self._start_node_installation(message, session, lang, user_id)

        except Exception as e:
            logger.error(f"Error handling install input: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('error_occurred', lang, error=str(e))
            )

            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]

    def _continue_to_port_config(self, message, session, lang):
        """Continue to port configuration"""
        session['step'] = 'port_config'

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(
                get_text('custom_ports', lang),
                callback_data='install_ports_custom'
            ),
            InlineKeyboardButton(
                get_text('random_ports', lang),
                callback_data='install_ports_random'
            )
        )

        self.bot.send_message(
            message.chat.id,
            get_text('port_config', lang),
            reply_markup=keyboard
        )

    def _generate_random_name(self):
        """Generate random node name"""
        return f"node-{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

    def _start_node_installation(self, message, session, lang, user_id):
        """Start the actual node installation process"""
        try:
            self.bot.send_message(
                message.chat.id,
                get_text('installing_node', lang)
            )

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
                db=self.db
            )

            if success:
                self.bot.send_message(
                    message.chat.id,
                    get_text('node_installed', lang)
                )
            else:
                self.bot.send_message(
                    message.chat.id,
                    get_text('installation_failed', lang, error=result)
                )

        except Exception as e:
            logger.error(f"Error during node installation: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('installation_failed', lang, error=str(e))
            )
        finally:
            # Clear session
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]

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

        # Authentication method callbacks  
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('install_auth_'))
        def install_auth_callback(call):
            user_id = call.from_user.id
            if user_id in self.bot.active_sessions:
                session = self.bot.active_sessions[user_id]
                user = self.db.get_user(user_id)
                lang = user['language'] if user else 'en'

                if call.data == 'install_auth_password':
                    session['step'] = 'ssh_password'
                    self.bot.edit_message_text(
                        get_text('enter_ssh_password', lang),
                        call.message.chat.id,
                        call.message.message_id
                    )
                elif call.data == 'install_auth_key':
                    session['step'] = 'ssh_key'
                    self.bot.edit_message_text(
                        get_text('enter_ssh_key', lang),
                        call.message.chat.id,
                        call.message.message_id
                    )

        # Port configuration callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('install_ports_'))
        def install_ports_callback(call):
            user_id = call.from_user.id
            if user_id in self.bot.active_sessions:
                session = self.bot.active_sessions[user_id]
                user = self.db.get_user(user_id)
                lang = user['language'] if user else 'en'

                if call.data == 'install_ports_custom':
                    session['step'] = 'node_port'
                    self.bot.edit_message_text(
                        get_text('enter_node_port', lang),
                        call.message.chat.id,
                        call.message.message_id
                    )
                elif call.data == 'install_ports_random':
                    import random
                    session['data']['node_port'] = random.randint(60000, 65000)
                    session['data']['api_port'] = random.randint(60000, 65000)
                    session['step'] = 'node_name'
                    self.bot.edit_message_text(
                        get_text('enter_node_name', lang),
                        call.message.chat.id,
                        call.message.message_id
                    )
