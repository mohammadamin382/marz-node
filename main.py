#!/usr/bin/env python3
"""
Marzban Node Management Bot
Main entry point for the Telegram bot
"""

import asyncio
import logging
from bot.core.bot import MarzNodeBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to start the bot"""
    bot = MarzNodeBot()
    bot.start()

if __name__ == "__main__":
    main()
