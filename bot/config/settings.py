"""
Bot configuration settings
"""

import os
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
DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')

# SSH connection settings
SSH_TIMEOUT = int(os.getenv('SSH_TIMEOUT', '30'))
MAX_SSH_RETRIES = int(os.getenv('MAX_SSH_RETRIES', '3'))

# API settings
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
MAX_API_RETRIES = int(os.getenv('MAX_API_RETRIES', '3'))

# Node installation settings
DEFAULT_NODE_PORT = int(os.getenv('DEFAULT_NODE_PORT', '62050'))
DEFAULT_API_PORT = int(os.getenv('DEFAULT_API_PORT', '62051'))

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'fa', 'ru', 'ar']
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')

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

# Installation commands
INSTALL_COMMANDS = [
    "apt-get update",
    "apt-get upgrade -y",
    "apt-get install curl socat git -y",
    "curl -fsSL https://get.docker.com | sh",
    "git clone https://github.com/Gozargah/Marzban-node",
    "mkdir -p /var/lib/marzban-node",
]
