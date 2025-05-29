"""
Panel management handler
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.db_manager import DatabaseManager
from bot.texts.bot_texts import get_text
from bot.services.marzban_api import MarzbanAPI
from bot.utils.decorators import admin_only
import logging
import re

logger = logging.getLogger(__name__)

class PanelHandler:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db
        self.marzban_api = MarzbanAPI()
    
    @admin_only
    def handle_add_panel(self, call):
        """Handle add panel request"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        # Show panel type selection
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(
            get_text('marzban_panel', lang),
            callback_data='panel_type_marzban'
        ))
        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data='panel_back_main'
        ))
        
        self.bot.edit_message_text(
            get_text('panel_type', lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
    
    def handle_callback(self, call):
        """Handle panel-related callbacks"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        if call.data == 'panel_type_marzban':
            self._start_panel_setup(call, 'marzban', lang)
        elif call.data == 'panel_back_main':
            from bot.handlers.start_handler import StartHandler
            start_handler = StartHandler(self.bot, self.db)
            start_handler.show_main_menu(call.message, lang)
    
    def _start_panel_setup(self, call, panel_type, lang):
        """Start panel setup process"""
        # Store session data
        user_id = call.from_user.id
        session_data = {
            'step': 'url',
            'panel_type': panel_type,
            'data': {},
            'handler': self._handle_panel_input
        }
        
        # Store in bot's active sessions
        self.bot.active_sessions = getattr(self.bot, 'active_sessions', {})
        self.bot.active_sessions[user_id] = session_data
        
        self.bot.edit_message_text(
            get_text('enter_panel_url', lang),
            call.message.chat.id,
            call.message.message_id
        )
    
    def _handle_panel_input(self, message, session):
        """Handle panel setup input"""
        user = self.db.get_user(message.from_user.id)
        lang = user['language'] if user else 'fa'
        user_id = message.from_user.id
        
        try:
            logger.info(f"Processing panel input for step: {session['step']}")
            
            if session['step'] == 'url':
                url = message.text.strip()
                logger.info(f"Processing URL: {url}")
                
                if not self._validate_url(url):
                    self.bot.send_message(
                        message.chat.id,
                        get_text('invalid_url', lang)
                    )
                    return
                
                session['data']['url'] = url
                session['step'] = 'username'
                
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_username', lang)
                )
                logger.info("URL saved, asking for username")
            
            elif session['step'] == 'username':
                username = message.text.strip()
                logger.info(f"Processing username: {username}")
                
                session['data']['username'] = username
                session['step'] = 'password'
                
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_password', lang)
                )
                logger.info("Username saved, asking for password")
            
            elif session['step'] == 'password':
                password = message.text.strip()
                logger.info("Processing password")
                
                session['data']['password'] = password
                session['step'] = 'name'
                
                self.bot.send_message(
                    message.chat.id,
                    get_text('enter_panel_name', lang)
                )
                logger.info("Password saved, asking for panel name")
            
            elif session['step'] == 'name':
                name = message.text.strip()
                logger.info(f"Processing panel name: {name}")
                
                session['data']['name'] = name
                
                # Show loading message
                loading_msg = self.bot.send_message(
                    message.chat.id,
                    "🔄 در حال تست اتصال..."
                )
                
                # Test connection and save panel
                self._test_and_save_panel(message, session, lang, user_id, loading_msg)
                
                # Clear session
                if hasattr(self.bot, 'active_sessions') and user_id in self.bot.active_sessions:
                    del self.bot.active_sessions[user_id]
                    logger.info("Session cleared")
        
        except Exception as e:
            logger.error(f"Error handling panel input: {e}")
            self.bot.send_message(
                message.chat.id,
                get_text('error_occurred', lang, error=str(e))
            )
            
            # Clear session
            if hasattr(self.bot, 'active_sessions') and user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]
    
    def _validate_url(self, url):
        """Validate panel URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    def _test_and_save_panel(self, message, session, lang, user_id, loading_msg=None):
        """Test panel connection and save if successful"""
        try:
            data = session['data']
            logger.info(f"Testing panel connection for: {data['url']}")
            
            # Delete loading message
            if loading_msg:
                try:
                    self.bot.delete_message(message.chat.id, loading_msg.message_id)
                except:
                    pass
            
            # Test connection
            success, token_data = self.marzban_api.authenticate(
                data['url'],
                data['username'],
                data['password']
            )
            
            logger.info(f"Authentication result: success={success}, token_data={token_data}")
            
            if success and token_data:
                # Save panel
                panel_id = self.db.add_panel(
                    name=data['name'],
                    url=data['url'],
                    username=data['username'],
                    password=data['password'],
                    panel_type=session['panel_type'],
                    added_by=user_id
                )
                
                logger.info(f"Panel saved with ID: {panel_id}")
                
                if panel_id and token_data:
                    # Save token
                    self.db.update_panel_token(
                        panel_id,
                        token_data.get('access_token'),
                        token_data.get('expires_at')
                    )
                    logger.info("Token saved")
                
                # Send success message with main menu
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton(
                    get_text('main_menu', lang),
                    callback_data='panel_back_main'
                ))
                
                self.bot.send_message(
                    message.chat.id,
                    get_text('panel_saved', lang),
                    reply_markup=keyboard
                )
            else:
                # Send detailed error message
                error_msg = "اتصال به پنل ناموفق بود."
                if isinstance(token_data, dict) and 'detail' in token_data:
                    error_msg += f"\nجزئیات: {token_data['detail']}"
                elif token_data:
                    error_msg += f"\nخطا: {str(token_data)}"
                
                # Add back to main menu button
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton(
                    get_text('main_menu', lang),
                    callback_data='panel_back_main'
                ))
                
                self.bot.send_message(
                    message.chat.id,
                    error_msg,
                    reply_markup=keyboard
                )
        
        except Exception as e:
            logger.error(f"Error testing panel connection: {e}")
            
            # Delete loading message
            if loading_msg:
                try:
                    self.bot.delete_message(message.chat.id, loading_msg.message_id)
                except:
                    pass
            
            # Add back to main menu button
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(
                get_text('main_menu', lang),
                callback_data='panel_back_main'
            ))
            
            self.bot.send_message(
                message.chat.id,
                f"خطا در تست اتصال: {str(e)}",
                reply_markup=keyboard
            )
