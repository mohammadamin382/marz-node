"""
Bot configuration settings
"""

import os
import logging
from typing import List
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file
load_env_file()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Bot token - get from environment
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set in environment variables or .env file")

# Admin user IDs - get from environment (comma-separated)
admin_ids_str = os.getenv('ADMIN_IDS', '')
ADMIN_IDS: List[int] = []
if admin_ids_str:
    try:
        ADMIN_IDS = [int(uid.strip()) for uid in admin_ids_str.split(',') if uid.strip()]
    except ValueError:
        print("Warning: Invalid ADMIN_IDS format in environment variables")

# Database settings
DATABASE_PATH = os.getenv('DATABASE_PATH') or 'bot_database.db'

# SSH connection settings  
SSH_TIMEOUT = int(os.getenv('SSH_TIMEOUT') or '30')
MAX_SSH_RETRIES = int(os.getenv('MAX_SSH_RETRIES') or '3')

# API settings
API_TIMEOUT = int(os.getenv('API_TIMEOUT') or '30')
MAX_API_RETRIES = int(os.getenv('MAX_API_RETRIES') or '3')

# Node installation settings - FIXED PORTS
FIXED_NODE_PORT = int(os.getenv('DEFAULT_NODE_PORT') or '62050')
FIXED_API_PORT = int(os.getenv('DEFAULT_API_PORT') or '62051')
DEFAULT_NODE_PORT = FIXED_NODE_PORT  # Keep for backward compatibility
DEFAULT_API_PORT = FIXED_API_PORT    # Keep for backward compatibility

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'fa', 'ru', 'ar']
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE') or 'en'

# Installation settings
INSTALL_ENABLED = (os.getenv('INSTALL_ENABLED') or 'false').lower() == 'true'

# Docker compose content for Marzban node
DOCKER_COMPOSE_CONTENT = """services:
  marzban-node:
    # build: .
    image: gozargah/marzban-node:latest
    restart: always
    network_mode: host

    environment:
      SSL_CLIENT_CERT_FILE: "/var/lib/marzban-node/ssl_client_cert.pem"

    volumes:
      - /var/lib/marzban-node:/var/lib/marzban-node
"""

# Installation commands with enhanced error prevention
INSTALL_COMMANDS = [
    # Comprehensive system preparation
    "export DEBIAN_FRONTEND=noninteractive",
    # Kill any hanging processes and clean up (gracefully handle if no processes exist)
    "pkill -f dpkg 2>/dev/null || true",
    "pkill -f apt 2>/dev/null || true", 
    "while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do echo 'Waiting for package managers...'; sleep 3; done || true",
    # Remove all possible lock files
    "rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock || true",
    # Fix any interrupted dpkg operations
    "dpkg --configure -a || true",
    # Clean and update package cache
    "apt-get clean && apt-get autoclean",
    "apt-get update",
    # Install packages with error handling
    "apt-get upgrade -y -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'",
    "apt-get install curl socat git -y -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'",
    # Install Docker
    "curl -fsSL https://get.docker.com | sh",
    # Clone Marzban-node
    "git clone https://github.com/Gozargah/Marzban-node || true",
    # Create directory
    "mkdir -p /var/lib/marzban-node",
]
