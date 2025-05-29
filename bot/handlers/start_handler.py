
"""
Start command and language selection handler
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.db_manager import DatabaseManager
from bot.texts.bot_texts import get_text, SUPPORTED_LANGUAGES
from bot.utils.decorators import admin_only
import logging

logger = logging.getLogger(__name__)

class StartHandler:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db
    
    def handle_start(self, message):
        """Handle /start command"""
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        
        # Check if user exists
        user = self.db.get_user(user_id)
        
        if not user:
            # New user - show language selection
            self.show_language_selection(message)
        else:
            # Existing user - show main menu
            self.show_main_menu(message, user['language'])
    
    def show_language_selection(self, message):
        """Show language selection menu"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        # Language options
        languages = {
            'en': '🇺🇸 English',
            'fa': '🇮🇷 فارسی',
            'ru': '🇷🇺 Русский',
            'ar': '🇸🇦 العربية'
        }
        
        buttons = []
        for lang_code, lang_name in languages.items():
            buttons.append(InlineKeyboardButton(
                lang_name, 
                callback_data=f'lang_{lang_code}'
            ))
        
        # Add buttons in rows of 2
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.row(buttons[i], buttons[i + 1])
            else:
                keyboard.row(buttons[i])
        
        self.bot.send_message(
            message.chat.id,
            get_text('select_language', 'en'),
            reply_markup=keyboard
        )
    
    def handle_language_selection(self, call):
        """Handle language selection callback"""
        lang_code = call.data.split('_')[1]
        user_id = call.from_user.id
        username = call.from_user.username
        first_name = call.from_user.first_name
        last_name = call.from_user.last_name
        
        # Save user with selected language
        self.db.add_user(user_id, username, first_name, last_name, lang_code)
        
        # Send confirmation
        self.bot.edit_message_text(
            get_text('language_selected', lang_code),
            call.message.chat.id,
            call.message.message_id
        )
        
        # Show main menu
        self.show_main_menu(call.message, lang_code)
    
    def show_main_menu(self, message, lang='en'):
        """Show main menu"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        # Main menu buttons
        buttons = [
            InlineKeyboardButton(
                get_text('add_panel', lang),
                callback_data='main_add_panel'
            ),
            InlineKeyboardButton(
                get_text('manage_nodes', lang),
                callback_data='main_manage_nodes'
            ),
            InlineKeyboardButton(
                get_text('admin_panel', lang),
                callback_data='main_admin_panel'
            ),
            InlineKeyboardButton(
                get_text('backup_data', lang),
                callback_data='main_backup'
            ),
            InlineKeyboardButton(
                get_text('statistics', lang),
                callback_data='main_stats'
            )
        ]
        
        # Add buttons in rows of 2
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.row(buttons[i], buttons[i + 1])
            else:
                keyboard.row(buttons[i])
        
        text = f"{get_text('welcome', lang)}\n\n{get_text('main_menu_desc', lang)}"
        
        try:
            # Try to edit if this is a callback
            if hasattr(message, 'message_id'):
                self.bot.edit_message_text(
                    text,
                    message.chat.id,
                    message.message_id,
                    reply_markup=keyboard
                )
            else:
                self.bot.send_message(
                    message.chat.id,
                    text,
                    reply_markup=keyboard
                )
        except:
            # Fallback to sending new message
            self.bot.send_message(
                message.chat.id,
                text,
                reply_markup=keyboard
            )
