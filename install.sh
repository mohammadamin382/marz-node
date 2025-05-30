
#!/bin/bash

# Colors for better UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Logo and welcome message
echo -e "${PURPLE}${BOLD}"
cat << "EOF"
███╗   ███╗ █████╗ ██████╗ ███████╗    ███╗   ██╗ ██████╗ ██████╗ ███████╗
████╗ ████║██╔══██╗██╔══██╗╚══███╔╝    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
██╔████╔██║███████║██████╔╝  ███╔╝     ██╔██╗ ██║██║   ██║██║  ██║█████╗  
██║╚██╔╝██║██╔══██║██╔══██╗ ███╔╝      ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
██║ ╚═╝ ██║██║  ██║██║  ██║███████╗    ██║ ╚████║╚██████╔╝██████╔╝███████╗
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
                                                                           
                    🤖 TELEGRAM BOT INSTALLER 🤖
EOF
echo -e "${NC}"

echo -e "${CYAN}${BOLD}========================================================================${NC}"
echo -e "${GREEN}${BOLD}              Welcome to Marzban Node Bot Installer                   ${NC}"
echo -e "${GREEN}                          Setup & Configuration Tool                       ${NC}"
echo -e "${CYAN}${BOLD}========================================================================${NC}"
echo

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

print_step() {
    echo -e "\n${BLUE}${BOLD}[STEP $1] ${2}${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}${BOLD}✅ ${1}${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}${BOLD}❌ ${1}${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}${BOLD}⚠️  ${1}${NC}"
}

# Function to print info
print_info() {
    echo -e "${CYAN}💡 ${1}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate Telegram bot token
validate_bot_token() {
    local token=$1
    if [[ $token =~ ^[0-9]+:[a-zA-Z0-9_-]+$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate admin IDs
validate_admin_ids() {
    local ids=$1
    if [[ $ids =~ ^[0-9]+(,[0-9]+)*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to create loading animation
show_loading() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_warning "It's recommended to run this script with a regular user, not root"
    echo -e "${YELLOW}Running as root may cause permission issues.${NC}"
    read -p "Are you sure you want to continue? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Exiting installer. Please run with a regular user account."
        exit 1
    fi
fi

print_step 1 "Checking Prerequisites & Dependencies"

# Check for Docker
if ! command_exists docker; then
    print_error "Docker not found. Installing Docker..."
    print_info "This may take a few minutes depending on your internet connection"
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    print_success "Docker successfully installed"
    print_warning "Please restart your system or re-login for changes to take effect"
    print_info "You may need to run 'newgrp docker' or logout and login again"
else
    print_success "Docker is already installed"
fi

# Check for Docker Compose
if ! command_exists docker-compose && ! docker compose version > /dev/null 2>&1; then
    print_error "Docker Compose not found. Installing..."
    
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is available"
fi

print_success "All prerequisites are satisfied"

print_step 2 "Configuration Setup & Bot Details"

# Get bot token
while true; do
    echo -e "\n${CYAN}${BOLD}Please enter your Telegram Bot Token:${NC}"
    echo -e "${YELLOW}📋 You can get this from @BotFather on Telegram${NC}"
    echo -e "${YELLOW}📝 Format: 123456789:ABCDEfghIJKLmnoPQRSTuvwxyz${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────${NC}"
    read -p "🤖 Bot Token: " BOT_TOKEN
    
    if validate_bot_token "$BOT_TOKEN"; then
        print_success "Valid bot token provided"
        break
    else
        print_error "Invalid token format. Please try again"
        print_info "Token should be in format: NUMBER:LETTERS_AND_NUMBERS"
    fi
done

# Get admin IDs
while true; do
    echo -e "\n${CYAN}${BOLD}Please enter Admin User IDs:${NC}"
    echo -e "${YELLOW}👑 These users will have full bot access${NC}"
    echo -e "${YELLOW}📝 Format: Comma-separated numbers (e.g., 123456789,987654321)${NC}"
    echo -e "${YELLOW}💡 To get your ID, message @userinfobot on Telegram${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────${NC}"
    read -p "👑 Admin IDs: " ADMIN_IDS
    
    if validate_admin_ids "$ADMIN_IDS"; then
        print_success "Valid admin IDs provided"
        break
    else
        print_error "Invalid ID format. Use only numbers and commas"
        print_info "Example: 123456789,987654321,555666777"
    fi
done

# Get optional settings
echo -e "\n${CYAN}${BOLD}Optional Configuration Settings:${NC}"
echo -e "${BLUE}────────────────────────────────────────────────${NC}"

read -p "🔌 Default Node Port (default: 62050): " NODE_PORT
NODE_PORT=${NODE_PORT:-62050}

read -p "🌐 Default API Port (default: 62051): " API_PORT
API_PORT=${API_PORT:-62051}

echo -e "\n${CYAN}${BOLD}Select Default Language:${NC}"
echo -e "${BLUE}────────────────────────────────────────────────${NC}"
echo "1) 🇮🇷 Persian (fa)"
echo "2) 🇺🇸 English (en)"
echo "3) 🇷🇺 Russian (ru)"
echo "4) 🇸🇦 Arabic (ar)"
read -p "Choose language (1-4) [1]: " LANG_CHOICE
case $LANG_CHOICE in
    2) DEFAULT_LANG="en" ;;
    3) DEFAULT_LANG="ru" ;;
    4) DEFAULT_LANG="ar" ;;
    *) DEFAULT_LANG="fa" ;;
esac

print_step 3 "Project Setup & Repository Clone"

# Remove existing directory if it exists
if [ -d "marz-node" ]; then
    print_warning "Existing directory found. Removing..."
    rm -rf marz-node
fi

# Clone the repository
print_info "Cloning from GitHub repository..."
if git clone https://github.com/mohammadamin382/marz-node.git; then
    print_success "Project successfully cloned"
else
    print_error "Failed to clone repository"
    print_info "Please check your internet connection and try again"
    exit 1
fi

cd marz-node

print_step 4 "Environment Configuration"

# Create .env file
print_info "Creating environment configuration file..."
cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=$BOT_TOKEN

# Admin User IDs (comma-separated)
ADMIN_IDS=$ADMIN_IDS

# Database Configuration
DATABASE_PATH=bot_database.db

# SSH Settings
SSH_TIMEOUT=30
MAX_SSH_RETRIES=3

# API Settings
API_TIMEOUT=30
MAX_API_RETRIES=3

# Node Installation Settings
DEFAULT_NODE_PORT=$NODE_PORT
DEFAULT_API_PORT=$API_PORT

# Language Settings
DEFAULT_LANGUAGE=$DEFAULT_LANG

# Installation Settings
INSTALL_ENABLED=true
EOF

print_success "Environment file created successfully"

print_step 5 "Directory Structure Setup"

# Create necessary directories
print_info "Creating required directories..."
mkdir -p data logs

print_success "Directory structure created"

print_step 6 "Docker Container Build & Deployment"

print_info "This step may take several minutes depending on your system..."
echo -e "${YELLOW}Please be patient while we build and start the container...${NC}"

# Build and run with docker-compose
if docker-compose up -d --build; then
    print_success "Container built and started successfully"
else
    print_error "Failed to build or start container"
    print_info "Check the logs above for more details"
    exit 1
fi

print_step 7 "Health Check & Status Verification"

# Wait a bit for container to start
print_info "Waiting for container to initialize..."
sleep 5

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    print_success "Bot is running successfully!"
    
    echo -e "\n${GREEN}${BOLD}========================================================================${NC}"
    echo -e "${GREEN}${BOLD}                    🎉 INSTALLATION COMPLETED! 🎉                       ${NC}"
    echo -e "${GREEN}${BOLD}                  Your Telegram Bot is Ready to Use                    ${NC}"
    echo -e "${GREEN}${BOLD}========================================================================${NC}"
    echo
    
    echo -e "${CYAN}${BOLD}📋 Important Information:${NC}"
    echo -e "${YELLOW}• ✅ Bot is running in the background${NC}"
    echo -e "${YELLOW}• 📁 Logs are saved in the 'logs' directory${NC}"
    echo -e "${YELLOW}• 💾 Database is stored in the 'data' directory${NC}"
    echo -e "${YELLOW}• 🔧 Configuration is in the '.env' file${NC}"
    echo
    
    echo -e "${CYAN}${BOLD}🛠️  Useful Commands:${NC}"
    echo -e "${BLUE}• View logs:          ${YELLOW}docker-compose logs -f${NC}"
    echo -e "${BLUE}• Stop bot:           ${YELLOW}docker-compose down${NC}"
    echo -e "${BLUE}• Restart bot:        ${YELLOW}docker-compose restart${NC}"
    echo -e "${BLUE}• Update bot:         ${YELLOW}git pull && docker-compose up -d --build${NC}"
    echo -e "${BLUE}• Check status:       ${YELLOW}docker-compose ps${NC}"
    echo
    
    echo -e "${GREEN}${BOLD}🚀 Next Steps:${NC}"
    echo -e "${CYAN}1. Open Telegram and find your bot${NC}"
    echo -e "${CYAN}2. Send /start to begin using the bot${NC}"
    echo -e "${CYAN}3. Add your first Marzban panel${NC}"
    echo -e "${CYAN}4. Start managing your nodes!${NC}"
    echo
    
else
    print_error "Bot failed to start properly"
    print_info "Checking container logs for troubleshooting..."
    echo -e "${RED}Container Logs:${NC}"
    docker-compose logs
    echo
    print_info "Please check the error messages above and try running the installer again"
fi

echo -e "\n${PURPLE}${BOLD}────────────────────────────────────────────────────────────────────────${NC}"
echo -e "${PURPLE}${BOLD}Developed by: Mohammad Amin | GitHub: @mohammadamin382${NC}"
echo -e "${PURPLE}${BOLD}Repository: https://github.com/mohammadamin382/marz-node${NC}"
echo -e "${PURPLE}${BOLD}────────────────────────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}${BOLD}Thank you for using Marzban Node Bot! 🤖${NC}"
