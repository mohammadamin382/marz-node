
"""
Admin panel handler
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.db_manager import DatabaseManager
from bot.texts.bot_texts import get_text
from bot.utils.decorators import admin_only
import logging
import os

logger = logging.getLogger(__name__)

class AdminHandler:
    def __init__(self, bot: telebot.TeleBot, db: DatabaseManager):
        self.bot = bot
        self.db = db
    
    @admin_only
    def handle_admin_panel(self, call):
        """Handle admin panel access"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(
            get_text('statistics', lang),
            callback_data='admin_stats'
        ))
        keyboard.row(InlineKeyboardButton(
            get_text('backup_data', lang),
            callback_data='admin_backup'
        ))
        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data='admin_back_main'
        ))
        
        self.bot.edit_message_text(
            get_text('admin_panel', lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
    
    @admin_only
    def handle_backup(self, call):
        """Handle backup creation"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        try:
            backup_path = self.db.create_backup()
            if backup_path and os.path.exists(backup_path):
                with open(backup_path, 'rb') as backup_file:
                    self.bot.send_document(
                        call.message.chat.id,
                        backup_file,
                        caption=get_text('backup_created', lang)
                    )
                
                # Clean up backup file
                os.remove(backup_path)
            else:
                self.bot.answer_callback_query(
                    call.id,
                    get_text('error_occurred', lang),
                    show_alert=True
                )
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e)),
                show_alert=True
            )
    
    @admin_only
    def handle_stats(self, call):
        """Handle statistics display"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        try:
            stats = self.db.get_stats()
            
            stats_text = f"{get_text('stats_title', lang)}\n\n"
            stats_text += f"{get_text('total_panels', lang, count=stats.get('total_panels', 0))}\n"
            stats_text += f"{get_text('total_nodes', lang, count=stats.get('total_nodes', 0))}\n"
            stats_text += f"{get_text('active_sessions', lang, count=len(getattr(self.bot, 'active_sessions', {})))}\n"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton(
                get_text('back', lang),
                callback_data='admin_panel'
            ))
            
            self.bot.edit_message_text(
                stats_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang, error=str(e)),
                show_alert=True
            )
    
    def handle_callback(self, call):
        """Handle admin callbacks"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        if call.data == 'admin_stats':
            self.handle_stats(call)
        elif call.data == 'admin_backup':
            self.handle_backup(call)
        elif call.data == 'admin_back_main':
            from bot.handlers.start_handler import StartHandler
            start_handler = StartHandler(self.bot, self.db)
            start_handler.show_main_menu(call.message, lang)
