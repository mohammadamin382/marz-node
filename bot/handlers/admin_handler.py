
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
import sqlite3
import shutil
from datetime import datetime

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
        keyboard.row(
            InlineKeyboardButton(
                get_text('statistics', lang),
                callback_data='admin_stats'
            ),
            InlineKeyboardButton(
                get_text('backup_data', lang),
                callback_data='admin_backup'
            )
        )
        keyboard.row(
            InlineKeyboardButton(
                get_text('add_admin', lang),
                callback_data='admin_add_admin'
            ),
            InlineKeyboardButton(
                get_text('import_backup', lang),
                callback_data='admin_import_backup'
            )
        )
        keyboard.row(InlineKeyboardButton(
            get_text('back', lang),
            callback_data='back_to_main'
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
    
    @admin_only
    def handle_add_admin(self, call):
        """Handle adding new admin"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        # Initialize session for admin creation
        user_id = call.from_user.id
        if not hasattr(self.bot, 'active_sessions'):
            self.bot.active_sessions = {}
        
        self.bot.active_sessions[user_id] = {
            'type': 'add_admin',
            'step': 'permissions',
            'data': {
                'permissions': {
                    'can_manage_panels': False,
                    'can_manage_nodes': False,
                    'can_view_stats': False,
                    'can_backup': False,
                    'can_add_admins': False
                }
            },
            'handler': self._handle_add_admin_input
        }
        
        self._show_permissions_menu(call, lang)
    
    def _show_permissions_menu(self, call, lang):
        """Show permissions selection menu"""
        user_id = call.from_user.id
        session = self.bot.active_sessions.get(user_id)
        permissions = session['data']['permissions']
        
        keyboard = InlineKeyboardMarkup()
        
        # Permission buttons with toggle state
        for perm, enabled in permissions.items():
            status = "✅" if enabled else "⚪"
            text = f"{status} {get_text(perm, lang)}"
            keyboard.row(InlineKeyboardButton(
                text,
                callback_data=f'admin_perm_{perm}'
            ))
        
        keyboard.row(
            InlineKeyboardButton(
                get_text('confirm', lang),
                callback_data='admin_perm_confirm'
            ),
            InlineKeyboardButton(
                get_text('cancel', lang),
                callback_data='admin_perm_cancel'
            )
        )
        
        try:
            self.bot.edit_message_text(
                get_text('select_admin_permissions', lang),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error showing permissions menu: {e}")
    
    @admin_only
    def handle_import_backup(self, call):
        """Handle backup import request"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        # Initialize session for backup import
        user_id = call.from_user.id
        if not hasattr(self.bot, 'active_sessions'):
            self.bot.active_sessions = {}
        
        self.bot.active_sessions[user_id] = {
            'type': 'import_backup',
            'step': 'waiting_file',
            'data': {},
            'handler': self._handle_backup_import_input
        }
        
        try:
            self.bot.edit_message_text(
                get_text('send_backup_file', lang),
                call.message.chat.id,
                call.message.message_id
            )
        except Exception as e:
            logger.error(f"Error requesting backup file: {e}")
    
    def _handle_add_admin_input(self, message, session):
        """Handle admin addition input"""
        user = self.db.get_user(message.from_user.id)
        lang = user['language'] if user else 'en'
        
        if session['step'] == 'user_id':
            try:
                admin_id = int(message.text.strip())
                
                # Check if user already exists
                existing_user = self.db.get_user(admin_id)
                if existing_user and existing_user.get('is_admin', False):
                    self.bot.send_message(
                        message.chat.id,
                        get_text('user_already_admin', lang)
                    )
                    return
                
                # Add admin with permissions
                permissions = session['data']['permissions']
                success = self.db.add_admin(admin_id, permissions)
                
                if success:
                    self.bot.send_message(
                        message.chat.id,
                        get_text('admin_added_successfully', lang, user_id=admin_id)
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        get_text('error_adding_admin', lang)
                    )
                
                # Clear session
                if message.from_user.id in self.bot.active_sessions:
                    del self.bot.active_sessions[message.from_user.id]
                
            except ValueError:
                self.bot.send_message(
                    message.chat.id,
                    get_text('invalid_user_id', lang)
                )
    
    def _handle_backup_import_input(self, message, session):
        """Handle backup import input"""
        user = self.db.get_user(message.from_user.id)
        lang = user['language'] if user else 'en'
        
        if session['step'] == 'waiting_file':
            if message.document and message.document.file_name.endswith('.db'):
                try:
                    # Download backup file
                    file_info = self.bot.get_file(message.document.file_id)
                    downloaded_file = self.bot.download_file(file_info.file_path)
                    
                    # Save temporary file
                    temp_backup_path = f"temp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    with open(temp_backup_path, 'wb') as f:
                        f.write(downloaded_file)
                    
                    session['data']['backup_path'] = temp_backup_path
                    session['step'] = 'merge_option'
                    
                    # Show merge options
                    keyboard = InlineKeyboardMarkup()
                    keyboard.row(
                        InlineKeyboardButton(
                            get_text('merge_databases', lang),
                            callback_data='backup_merge'
                        ),
                        InlineKeyboardButton(
                            get_text('replace_database', lang),
                            callback_data='backup_replace'
                        )
                    )
                    keyboard.row(InlineKeyboardButton(
                        get_text('cancel', lang),
                        callback_data='backup_cancel'
                    ))
                    
                    self.bot.send_message(
                        message.chat.id,
                        get_text('choose_import_method', lang),
                        reply_markup=keyboard
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing backup file: {e}")
                    self.bot.send_message(
                        message.chat.id,
                        get_text('error_processing_backup', lang, error=str(e))
                    )
            else:
                self.bot.send_message(
                    message.chat.id,
                    get_text('invalid_backup_file', lang)
                )
    
    def _merge_databases(self, backup_path: str, user_id: int) -> bool:
        """Merge backup database with current database"""
        user = self.db.get_user(user_id)
        lang = user['language'] if user else 'en'
        
        try:
            # Connect to both databases
            backup_conn = sqlite3.connect(backup_path)
            current_conn = sqlite3.connect(self.db.db_path)
            
            backup_cursor = backup_conn.cursor()
            current_cursor = current_conn.cursor()
            
            conflicts = []
            
            # Check for panel conflicts
            backup_cursor.execute("SELECT * FROM panels")
            backup_panels = backup_cursor.fetchall()
            
            for panel in backup_panels:
                current_cursor.execute(
                    "SELECT * FROM panels WHERE url = ? AND username = ?",
                    (panel[2], panel[3])
                )
                existing = current_cursor.fetchone()
                
                if existing:
                    conflicts.append({
                        'type': 'panel',
                        'backup_data': panel,
                        'current_data': existing
                    })
                else:
                    # Insert non-conflicting panel
                    current_cursor.execute('''
                        INSERT INTO panels (name, url, username, password, panel_type, added_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (panel[1], panel[2], panel[3], panel[4], panel[5], panel[8]))
            
            # Handle conflicts if any
            if conflicts:
                self._handle_merge_conflicts(conflicts, user_id, lang, backup_conn, current_conn)
                return False  # Will handle async
            else:
                current_conn.commit()
                backup_conn.close()
                current_conn.close()
                
                self.bot.send_message(
                    user_id,
                    get_text('backup_merged_successfully', lang)
                )
                return True
                
        except Exception as e:
            logger.error(f"Error merging databases: {e}")
            self.bot.send_message(
                user_id,
                get_text('error_merging_backup', lang, error=str(e))
            )
            return False
    
    def _handle_merge_conflicts(self, conflicts, user_id, lang, backup_conn, current_conn):
        """Handle merge conflicts by asking user"""
        if not hasattr(self.bot, 'active_sessions'):
            self.bot.active_sessions = {}
        
        self.bot.active_sessions[user_id] = {
            'type': 'resolve_conflicts',
            'data': {
                'conflicts': conflicts,
                'current_conflict': 0,
                'backup_conn': backup_conn,
                'current_conn': current_conn
            },
            'handler': self._handle_conflict_resolution
        }
        
        self._show_conflict_resolution(user_id, lang)
    
    def _show_conflict_resolution(self, user_id, lang):
        """Show conflict resolution options"""
        session = self.bot.active_sessions[user_id]
        conflicts = session['data']['conflicts']
        current_idx = session['data']['current_conflict']
        
        if current_idx >= len(conflicts):
            # All conflicts resolved
            self._finish_merge(user_id, lang)
            return
        
        conflict = conflicts[current_idx]
        
        if conflict['type'] == 'panel':
            backup_panel = conflict['backup_data']
            current_panel = conflict['current_data']
            
            text = get_text('panel_conflict_detected', lang,
                          backup_name=backup_panel[1],
                          current_name=current_panel[1],
                          url=backup_panel[2])
            
            keyboard = InlineKeyboardMarkup()
            keyboard.row(
                InlineKeyboardButton(
                    get_text('replace_with_backup', lang),
                    callback_data='conflict_replace'
                ),
                InlineKeyboardButton(
                    get_text('keep_current', lang),
                    callback_data='conflict_skip'
                )
            )
            
            self.bot.send_message(user_id, text, reply_markup=keyboard)
    
    def handle_callback(self, call):
        """Handle admin callbacks"""
        user = self.db.get_user(call.from_user.id)
        lang = user['language'] if user else 'en'
        
        if call.data == 'admin_stats':
            self.handle_stats(call)
        elif call.data == 'admin_backup':
            self.handle_backup(call)
        elif call.data == 'admin_add_admin':
            self.handle_add_admin(call)
        elif call.data == 'admin_import_backup':
            self.handle_import_backup(call)
        elif call.data.startswith('admin_perm_'):
            self._handle_permission_toggle(call)
        elif call.data.startswith('backup_'):
            self._handle_backup_action(call)
        elif call.data.startswith('conflict_'):
            self._handle_conflict_action(call)
        elif call.data == 'back_to_main':
            self._back_to_main_menu(call)
    
    def _handle_permission_toggle(self, call):
        """Handle permission toggle"""
        user_id = call.from_user.id
        session = self.bot.active_sessions.get(user_id)
        
        if not session or session['type'] != 'add_admin':
            return
        
        user = self.db.get_user(user_id)
        lang = user['language'] if user else 'en'
        
        if call.data == 'admin_perm_confirm':
            session['step'] = 'user_id'
            try:
                self.bot.edit_message_text(
                    get_text('enter_admin_user_id', lang),
                    call.message.chat.id,
                    call.message.message_id
                )
            except Exception as e:
                logger.error(f"Error requesting user ID: {e}")
        elif call.data == 'admin_perm_cancel':
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]
            self.handle_admin_panel(call)
        else:
            # Toggle permission
            perm_name = call.data.replace('admin_perm_', '')
            if perm_name in session['data']['permissions']:
                session['data']['permissions'][perm_name] = not session['data']['permissions'][perm_name]
                self._show_permissions_menu(call, lang)
    
    def _handle_backup_action(self, call):
        """Handle backup import actions"""
        user_id = call.from_user.id
        session = self.bot.active_sessions.get(user_id)
        
        if not session or session['type'] != 'import_backup':
            return
        
        user = self.db.get_user(user_id)
        lang = user['language'] if user else 'en'
        
        if call.data == 'backup_merge':
            backup_path = session['data']['backup_path']
            self._merge_databases(backup_path, user_id)
        elif call.data == 'backup_replace':
            self._replace_database(session['data']['backup_path'], user_id, lang)
        elif call.data == 'backup_cancel':
            # Clean up temp file
            if 'backup_path' in session['data']:
                try:
                    os.remove(session['data']['backup_path'])
                except:
                    pass
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]
            self.handle_admin_panel(call)
    
    def _replace_database(self, backup_path: str, user_id: int, lang: str):
        """Replace current database with backup"""
        try:
            # Create backup of current database
            current_backup = f"current_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db.db_path, current_backup)
            
            # Replace with backup
            shutil.copy2(backup_path, self.db.db_path)
            
            # Clean up temp file
            os.remove(backup_path)
            
            self.bot.send_message(
                user_id,
                get_text('database_replaced_successfully', lang, backup_file=current_backup)
            )
            
            # Clear session
            if user_id in self.bot.active_sessions:
                del self.bot.active_sessions[user_id]
                
        except Exception as e:
            logger.error(f"Error replacing database: {e}")
            self.bot.send_message(
                user_id,
                get_text('error_replacing_database', lang, error=str(e))
            )
    
    def _back_to_main_menu(self, call):
        """Go back to main menu"""
        try:
            from bot.handlers.start_handler import StartHandler
            start_handler = StartHandler(self.bot, self.db)
            user = self.db.get_user(call.from_user.id)
            lang = user['language'] if user else 'en'
            
            # Create a mock message object for show_main_menu
            mock_message = type('MockMessage', (), {
                'chat': type('MockChat', (), {'id': call.message.chat.id})(),
                'message_id': call.message.message_id
            })()
            
            # Delete current message and send new main menu
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            start_handler.show_main_menu(mock_message, lang)
            
        except Exception as e:
            logger.error(f"Error going back to main menu: {e}")
            self.bot.answer_callback_query(
                call.id,
                get_text('error_occurred', lang if 'lang' in locals() else 'en', error=str(e)),
                show_alert=True
            )
