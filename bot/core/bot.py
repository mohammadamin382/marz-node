"""
Main bot class and initialization
"""

import telebot
import threading
import logging
from typing import Dict, Any
from bot.config.settings import BOT_TOKEN, ADMIN_IDS
from bot.database.db_manager import DatabaseManager
from bot.handlers.start_handler import StartHandler
from bot.handlers.panel_handler import PanelHandler
from bot.handlers.node_handler import NodeHandler
from bot.handlers.admin_handler import AdminHandler
from bot.utils.decorators import admin_only

logger = logging.getLogger(__name__)

class MarzNodeBot:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.db = DatabaseManager()
        self.active_sessions = {}

        # Initialize handlers
        self.start_handler = StartHandler(self.bot, self.db)
        self.panel_handler = PanelHandler(self.bot, self.db)
        self.node_handler = NodeHandler(self.bot, self.db)
        self.admin_handler = AdminHandler(self.bot, self.db)

        self._register_handlers()

    def _register_handlers(self):
        """Register all bot handlers"""

        # Start command
        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            self.start_handler.handle_start(message)

        # Main menu callback
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('main_'))
        def main_menu_callback(call):
            if call.data == 'main_add_panel':
                self.panel_handler.handle_add_panel(call)
            elif call.data == 'main_manage_nodes':
                self.node_handler.handle_manage_nodes_menu(call)
            elif call.data == 'main_admin_panel':
                self.admin_handler.handle_admin_panel(call)
            elif call.data == 'main_backup':
                self.admin_handler.handle_backup(call)
            elif call.data == 'main_stats':
                self.admin_handler.handle_stats(call)

        # Panel management callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('panel_'))
        def panel_callback(call):
            self.panel_handler.handle_callback(call)

        # Node management callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('node_'))
        def node_callback(call):
            self.node_handler.handle_callback(call)

        # Install authentication callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('install_auth_'))
        def install_auth_callback(call):
            user_id = call.from_user.id

            # Make sure active_sessions exists
            if not hasattr(self.bot, 'active_sessions'):
                self.bot.active_sessions = {}

            session = self.bot.active_sessions.get(user_id)

            if session:
                from bot.texts.bot_texts import get_text
                user = self.db.get_user(call.from_user.id)
                lang = user['language'] if user else 'en'

                if call.data == 'install_auth_password':
                    session['step'] = 'ssh_password'
                    session['data']['auth_type'] = 'password'

                    try:
                        self.bot.edit_message_text(
                            get_text('enter_ssh_password', lang),
                            call.message.chat.id,
                            call.message.message_id
                        )
                    except Exception as e:
                        logger.error(f"Error in password auth callback: {e}")
                        self.bot.send_message(
                            call.message.chat.id,
                            get_text('enter_ssh_password', lang)
                        )

                elif call.data == 'install_auth_key':
                    session['step'] = 'ssh_key'
                    session['data']['auth_type'] = 'ssh_key'

                    try:
                        self.bot.edit_message_text(
                            get_text('enter_ssh_key', lang),
                            call.message.chat.id,
                            call.message.message_id
                        )
                    except Exception as e:
                        logger.error(f"Error in key auth callback: {e}")
                        self.bot.send_message(
                            call.message.chat.id,
                            get_text('enter_ssh_key', lang)
                        )
            else:
                # No active session - inform user to start over
                from bot.texts.bot_texts import get_text
                user = self.db.get_user(call.from_user.id)
                lang = user['language'] if user else 'en'
                self.bot.answer_callback_query(
                    call.id,
                    get_text('session_expired', lang),
                    show_alert=True
                )

        # Bulk authentication callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('bulk_auth_'))
        def bulk_auth_callback(call):
            user_id = call.from_user.id

            # Make sure active_sessions exists
            if not hasattr(self.bot, 'active_sessions'):
                self.bot.active_sessions = {}

            session = self.bot.active_sessions.get(user_id)

            if session:
                from bot.texts.bot_texts import get_text
                user = self.db.get_user(call.from_user.id)
                lang = user['language'] if user else 'en'

                if call.data == 'bulk_auth_password':
                    self.node_handler._handle_bulk_auth_choice(call, 'password', lang)
                elif call.data == 'bulk_auth_ssh':
                    self.node_handler._handle_bulk_auth_choice(call, 'ssh_key', lang)

        # Panel management callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('panel_'))
        def panel_callback(call):
            self.panel_handler.handle_callback(call)

        # Admin callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('admin_') or call.data.startswith('backup_') or call.data.startswith('conflict_'))
        def admin_callback(call):
            self.admin_handler.handle_callback(call)

        # Installation callbacks
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('install_'))
        def install_callback(call):
            user_id = call.from_user.id
            if hasattr(self.bot, 'active_sessions') and user_id in self.bot.active_sessions:
                session = self.bot.active_sessions[user_id]
                user = self.db.get_user(user_id)
                lang = user['language'] if user else 'en'

                try:
                    if call.data.startswith('install_ports_'):
                        if call.data == 'install_ports_custom':
                            session['step'] = 'node_port'
                            from bot.texts.bot_texts import get_text
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
                            from bot.texts.bot_texts import get_text
                            self.bot.edit_message_text(
                                get_text('enter_node_name', lang),
                                call.message.chat.id,
                                call.message.message_id
                            )
                except Exception as e:
                    logger.error(f"Error in install callback: {e}")
                    from bot.texts.bot_texts import get_text
                    self.bot.answer_callback_query(
                        call.id,
                        get_text('error_occurred', lang, error=str(e)),
                        show_alert=True
                    )

        # Language selection callback
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
        def language_callback(call):
            self.start_handler.handle_language_selection(call)

        # Back to main menu callback
        @self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
        def back_to_main_callback(call):
            try:
                user = self.db.get_user(call.from_user.id)
                lang = user['language'] if user else 'en'
                
                # Delete current message and show main menu
                try:
                    self.bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                
                # Create mock message for show_main_menu
                mock_message = type('MockMessage', (), {
                    'chat': type('MockChat', (), {'id': call.message.chat.id})()
                })()
                
                self.start_handler.show_main_menu(mock_message, lang)
                
            except Exception as e:
                logger.error(f"Error in back_to_main callback: {e}")
                from bot.texts.bot_texts import get_text
                user = self.db.get_user(call.from_user.id)
                lang = user['language'] if user else 'en'
                self.bot.answer_callback_query(
                    call.id,
                    get_text('error_occurred', lang, error=str(e)),
                    show_alert=True
                )

        # Text message handler for input collection  
        @self.bot.message_handler(func=lambda message: True, content_types=['text'])
        def handle_text(message):
            user_id = message.from_user.id

            # Make sure active_sessions exists
            if not hasattr(self.bot, 'active_sessions'):
                self.bot.active_sessions = {}

            if user_id in self.bot.active_sessions:
                session = self.bot.active_sessions[user_id]
                try:
                    session['handler'](message, session)
                except Exception as e:
                    logger.error(f"Error in session handler: {e}")
                    # Clear broken session
                    if user_id in self.bot.active_sessions:
                        del self.bot.active_sessions[user_id]

                    # Get user language and send error
                    user = self.db.get_user(user_id)
                    lang = user['language'] if user else 'fa'
                    from bot.texts.bot_texts import get_text
                    self.bot.send_message(
                        message.chat.id,
                        get_text('error_occurred', lang, error=str(e))
                    )

        # Document handler for backup files
        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            user_id = message.from_user.id

            # Make sure active_sessions exists
            if not hasattr(self.bot, 'active_sessions'):
                self.bot.active_sessions = {}

            if user_id in self.bot.active_sessions:
                session = self.bot.active_sessions[user_id]
                try:
                    session['handler'](message, session)
                except Exception as e:
                    logger.error(f"Error in document session handler: {e}")
                    # Clear broken session
                    if user_id in self.bot.active_sessions:
                        del self.bot.active_sessions[user_id]

                    # Get user language and send error
                    user = self.db.get_user(user_id)
                    lang = user['language'] if user else 'fa'
                    from bot.texts.bot_texts import get_text
                    self.bot.send_message(
                        message.chat.id,
                        get_text('error_occurred', lang, error=str(e))
                    )

    def start(self):
        """Start the bot"""
        logger.info("Starting Marzban Node Management Bot...")
        try:
            self.bot.infinity_polling(none_stop=True, interval=1)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
        finally:
            logger.info("Bot stopped")
