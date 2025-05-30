"""
Utility decorators for the bot
"""

import functools
import logging
from bot.config.settings import ADMIN_IDS

logger = logging.getLogger(__name__)

def admin_only(func):
    """Decorator to restrict access to admin users only"""
    @functools.wraps(func)
    def wrapper(self, call_or_message, *args, **kwargs):
        user_id = call_or_message.from_user.id
        
        if user_id not in ADMIN_IDS:
            # Check if user is admin in database
            user = self.db.get_user(user_id)
            if not user or not user.get('is_admin', False):
                # Send access denied message
                lang = user['language'] if user else 'en'
                from bot.texts.bot_texts import get_text
                
                if hasattr(call_or_message, 'message'):
                    # It's a callback query
                    self.bot.answer_callback_query(
                        call_or_message.id,
                        get_text('admin_only', lang),
                        show_alert=True
                    )
                else:
                    # It's a message
                    self.bot.send_message(
                        call_or_message.chat.id,
                        get_text('admin_only', lang)
                    )
                return
        
        return func(self, call_or_message, *args, **kwargs)
    
    return wrapper

def error_handler(func):
    """Decorator to handle errors gracefully"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            #######################################
            raise
    
    return wrapper
