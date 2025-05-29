
<div align="center">

# 🚀 Marzban Node Management Bot

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/marzban-node-bot?style=social)](https://github.com/yourusername/marzban-node-bot)

**🤖 Your friendly assistant for managing Marzban nodes with style!**

*Automate your Marzban node deployment and management through a powerful Telegram bot*

[🎯 Features](#-features) • [🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🌐 Languages](#-supported-languages) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 What is Marzban Node Bot?

Meet your new best friend for Marzban node management! This bot makes deploying and managing Marzban nodes as easy as sending a message. With support for 4 languages and a super friendly interface, you'll love how simple node management becomes.

### ✨ Why Choose Our Bot?

- 🎯 **Zero Complexity**: No command-line hassles, just friendly conversations
- 🌍 **Multilingual Support**: English, Persian, Russian, and Arabic
- 🔐 **Secure by Design**: Environment-based configuration and secure connections
- 📱 **Mobile-First**: Manage everything from your phone
- 🚀 **Lightning Fast**: Deploy nodes in minutes, not hours

---

## 🎨 Features

<div align="center">
  <table>
    <tr>
      <td align="center">
        <h3>🔧 Node Management</h3>
        <p>Create, monitor, and manage your Marzban nodes with just a few taps</p>
      </td>
      <td align="center">
        <h3>📊 Panel Integration</h3>
        <p>Seamlessly connect to multiple Marzban panels</p>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>🌐 Multi-Language</h3>
        <p>Available in English, Persian, Russian, and Arabic</p>
      </td>
      <td align="center">
        <h3>🔐 Secure SSH</h3>
        <p>Support for password and SSH key authentication</p>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>📦 Bulk Operations</h3>
        <p>Install nodes on multiple servers simultaneously</p>
      </td>
      <td align="center">
        <h3>💾 Data Management</h3>
        <p>Backup and restore your configurations</p>
      </td>
    </tr>
  </table>
</div>

### 🚀 Core Capabilities

- **🎯 Smart Node Deployment**: Automated Docker-based installation
- **📊 Real-time Monitoring**: Live status updates and health checks
- **🔄 Easy Reconnection**: One-click node reconnection
- **🗑️ Clean Management**: Remove nodes safely when needed
- **📈 Statistics Dashboard**: Track your infrastructure at a glance
- **💾 Backup System**: Never lose your configurations
- **👥 Multi-User Support**: Admin controls and user management

---

## 🚀 Quick Start

### 🔧 Prerequisites

- Python 3.11 or higher
- A Telegram bot token ([Get one from @BotFather](https://t.me/botfather))
- A server with SSH access for node installation

### ⚡ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/marzban-node-bot.git
   cd marzban-node-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Set up your bot token**
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   ADMIN_IDS=your_telegram_user_id
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

### 🎯 First Steps

1. Start a chat with your bot on Telegram
2. Send `/start` to begin
3. Choose your preferred language
4. Add your first Marzban panel
5. Start deploying nodes!

---

## 📖 Documentation

### 🛠️ Configuration

The bot uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```env
# Required
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321

# Optional
DATABASE_PATH=bot_database.db
DEFAULT_LANGUAGE=en
SSH_TIMEOUT=30
DEFAULT_NODE_PORT=62050
DEFAULT_API_PORT=62051
```

### 🔐 Security Features

- **Environment-based secrets**: No hardcoded credentials
- **Admin-only functions**: Restricted access to sensitive operations
- **Secure SSH connections**: Support for key-based authentication
- **Input validation**: Protection against malicious inputs

### 📱 Bot Commands

- `/start` - Initialize the bot and show main menu
- Language selection for new users
- Interactive menus for all operations

---

## 🌐 Supported Languages

<div align="center">
  <table>
    <tr>
      <td align="center">🇺🇸<br><strong>English</strong></td>
      <td align="center">🇮🇷<br><strong>فارسی</strong></td>
      <td align="center">🇷🇺<br><strong>Русский</strong></td>
      <td align="center">🇸🇦<br><strong>العربية</strong></td>
    </tr>
  </table>
</div>

The bot automatically detects your preference and provides a fully localized experience in your chosen language.

---

## 🏗️ Architecture

```
marzban-node-bot/
├── bot/
│   ├── core/           # Core bot functionality
│   ├── handlers/       # Message and callback handlers
│   ├── services/       # SSH, API, and external services
│   ├── database/       # Database management
│   ├── config/         # Configuration management
│   ├── texts/          # Multilingual text content
│   └── utils/          # Utility functions and decorators
├── main.py            # Application entry point
├── .env.example       # Environment template
└── requirements.txt   # Python dependencies
```

---

## 🚀 Deployment on Replit

This bot is optimized for Replit deployment:

1. Fork this repository to Replit
2. Set up your environment variables in Replit Secrets
3. Click the Run button
4. Your bot is live! 🎉

### 🔧 Replit Configuration

The bot includes pre-configured:
- `.replit` file for automatic environment setup
- `pyproject.toml` for dependency management
- Optimized for Replit's infrastructure

---

## 🤝 Contributing

We love contributions! Here's how you can help:

### 🐛 Found a Bug?

1. Check existing issues
2. Create a detailed bug report
3. Include steps to reproduce

### 💡 Have an Idea?

1. Open a feature request
2. Describe your use case
3. Let's discuss implementation

### 🔧 Want to Code?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### 🌍 Language Support

Help us expand language support:
- Add new languages to `bot/texts/bot_texts.py`
- Update the `SUPPORTED_LANGUAGES` list
- Test the translations

---

## 📋 Roadmap

- [ ] 🔄 Auto-update functionality
- [ ] 📊 Advanced analytics dashboard
- [ ] 🔔 Custom notification settings
- [ ] 🌐 Web interface companion
- [ ] 📱 Mobile app integration
- [ ] 🔗 API for third-party integrations

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💖 Support

Love this project? Here's how you can show support:

- ⭐ Star this repository
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 🔄 Share with friends
- ☕ [Buy me a coffee](https://buymeacoffee.com/yourusername)

---

## 📞 Get Help

- 📚 [Documentation](https://github.com/yourusername/marzban-node-bot/wiki)
- 💬 [Telegram Support Group](https://t.me/marzban_node_bot_support)
- 🐛 [Issue Tracker](https://github.com/yourusername/marzban-node-bot/issues)
- 📧 [Email Support](mailto:support@yourproject.com)

---

<div align="center">

**Made with ❤️ for the Marzban community**

*Star this repo if you find it useful! ⭐*

[🔝 Back to Top](#-marzban-node-management-bot)

</div>
