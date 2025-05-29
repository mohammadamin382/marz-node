#!/bin/bash

# Colors for UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="marzban-node-bot"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

# Function to print header
print_header() {
    clear
    print_color $CYAN "╔══════════════════════════════════════════════════════════════╗"
    print_color $CYAN "║                  🚀 Marzban Node Bot Manager 🚀               ║"
    print_color $CYAN "║                     Advanced Installation Tool               ║"
    print_color $CYAN "╚══════════════════════════════════════════════════════════════╝"
    echo
}

# Function to show loading animation
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker
install_docker() {
    print_color $YELLOW "🔧 Installing Docker..."
    if ! command_exists docker; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        print_color $GREEN "✅ Docker installed successfully!"
    else
        print_color $GREEN "✅ Docker already installed!"
    fi
}

# Function to install Docker Compose
install_docker_compose() {
    print_color $YELLOW "🔧 Installing Docker Compose..."
    if ! command_exists docker-compose; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_color $GREEN "✅ Docker Compose installed successfully!"
    else
        print_color $GREEN "✅ Docker Compose already installed!"
    fi
}

# Function to setup environment file
setup_environment() {
    print_header
    print_color $BLUE "🔧 Environment Configuration"
    echo
    
    if [ ! -f "$ENV_FILE" ]; then
        cp .env.example "$ENV_FILE"
        print_color $YELLOW "📝 Please configure your environment variables:"
        echo
        
        read -p "$(print_color $WHITE "Enter Telegram Bot Token: ")" bot_token
        read -p "$(print_color $WHITE "Enter Admin User IDs (comma-separated): ")" admin_ids
        read -p "$(print_color $WHITE "Enter Default Language (en/fa/ru/ar) [fa]: ")" default_lang
        default_lang=${default_lang:-fa}
        
        # Update .env file
        sed -i "s/your_telegram_bot_token_here/$bot_token/" "$ENV_FILE"
        sed -i "s/123456789,987654321/$admin_ids/" "$ENV_FILE"
        sed -i "s/DEFAULT_LANGUAGE=en/DEFAULT_LANGUAGE=$default_lang/" "$ENV_FILE"
        
        print_color $GREEN "✅ Environment configured successfully!"
    else
        print_color $GREEN "✅ Environment file already exists!"
    fi
}

# Function to show main menu
show_main_menu() {
    print_header
    print_color $WHITE "📋 Main Menu"
    echo
    print_color $CYAN "1.  🚀 Install & Start Bot"
    print_color $CYAN "2.  ⏹️  Stop Bot"
    print_color $CYAN "3.  🔄 Restart Bot"
    print_color $CYAN "4.  📊 Show Status"
    print_color $CYAN "5.  📋 Show Logs"
    print_color $CYAN "6.  🔧 Update Bot"
    print_color $CYAN "7.  ⚙️  Configure Environment"
    print_color $CYAN "8.  🗑️  Uninstall Bot"
    print_color $CYAN "9.  📦 Container Management"
    print_color $CYAN "10. 🔍 System Information"
    print_color $CYAN "11. 🛠️  Troubleshooting"
    print_color $RED "0.  ❌ Exit"
    echo
    read -p "$(print_color $WHITE "Select an option: ")" choice
}

# Function to install and start bot
install_start_bot() {
    print_header
    print_color $BLUE "🚀 Installing and Starting Marzban Node Bot"
    echo
    
    # Check dependencies
    install_docker
    install_docker_compose
    
    # Setup environment
    setup_environment
    
    # Create data directory
    mkdir -p data logs
    
    print_color $YELLOW "🔨 Building and starting bot..."
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Bot installed and started successfully!"
        print_color $CYAN "🌐 Bot is now running in the background"
    else
        print_color $RED "❌ Failed to start bot!"
    fi
    
    read -p "Press Enter to continue..."
}

# Function to stop bot
stop_bot() {
    print_header
    print_color $YELLOW "⏹️ Stopping bot..."
    docker-compose down
    print_color $GREEN "✅ Bot stopped successfully!"
    read -p "Press Enter to continue..."
}

# Function to restart bot
restart_bot() {
    print_header
    print_color $YELLOW "🔄 Restarting bot..."
    docker-compose restart
    print_color $GREEN "✅ Bot restarted successfully!"
    read -p "Press Enter to continue..."
}

# Function to show status
show_status() {
    print_header
    print_color $BLUE "📊 Bot Status"
    echo
    
    if docker-compose ps | grep -q "Up"; then
        print_color $GREEN "✅ Bot is running"
        echo
        docker-compose ps
    else
        print_color $RED "❌ Bot is not running"
    fi
    
    echo
    print_color $CYAN "Docker containers:"
    docker ps -a --filter "name=$PROJECT_NAME"
    
    read -p "Press Enter to continue..."
}

# Function to show logs
show_logs() {
    print_header
    print_color $BLUE "📋 Bot Logs"
    echo
    print_color $CYAN "1. Live logs (Ctrl+C to exit)"
    print_color $CYAN "2. Last 50 lines"
    print_color $CYAN "3. Last 100 lines"
    print_color $CYAN "4. Error logs only"
    echo
    read -p "Select option: " log_choice
    
    case $log_choice in
        1) docker-compose logs -f ;;
        2) docker-compose logs --tail=50 ;;
        3) docker-compose logs --tail=100 ;;
        4) docker-compose logs | grep -i error ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
}

# Function to update bot
update_bot() {
    print_header
    print_color $YELLOW "🔧 Updating bot..."
    
    # Pull latest changes
    git pull origin main
    
    # Rebuild and restart
    docker-compose down
    docker-compose up -d --build
    
    print_color $GREEN "✅ Bot updated successfully!"
    read -p "Press Enter to continue..."
}

# Function to configure environment
configure_environment() {
    print_header
    print_color $BLUE "⚙️ Environment Configuration"
    echo
    
    if [ -f "$ENV_FILE" ]; then
        print_color $CYAN "Current configuration:"
        cat "$ENV_FILE" | grep -v "^#" | grep -v "^$"
        echo
    fi
    
    print_color $YELLOW "1. Edit configuration file"
    print_color $YELLOW "2. Reset to default"
    print_color $YELLOW "3. Show current config"
    echo
    read -p "Select option: " config_choice
    
    case $config_choice in
        1) nano "$ENV_FILE" ;;
        2) cp .env.example "$ENV_FILE" && setup_environment ;;
        3) cat "$ENV_FILE" ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Function to uninstall bot
uninstall_bot() {
    print_header
    print_color $RED "🗑️ Uninstalling Bot"
    echo
    print_color $YELLOW "⚠️  This will remove all containers, images, and data!"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        print_color $YELLOW "Stopping and removing containers..."
        docker-compose down -v
        
        print_color $YELLOW "Removing images..."
        docker rmi $(docker images "*$PROJECT_NAME*" -q) 2>/dev/null
        
        print_color $YELLOW "Cleaning up..."
        docker system prune -f
        
        print_color $GREEN "✅ Bot uninstalled successfully!"
    else
        print_color $CYAN "Operation cancelled."
    fi
    
    read -p "Press Enter to continue..."
}

# Function for container management
container_management() {
    print_header
    print_color $BLUE "📦 Container Management"
    echo
    print_color $CYAN "1. List all containers"
    print_color $CYAN "2. Remove unused containers"
    print_color $CYAN "3. Clean up system"
    print_color $CYAN "4. Container resource usage"
    print_color $CYAN "5. Exec into container"
    echo
    read -p "Select option: " container_choice
    
    case $container_choice in
        1) docker ps -a ;;
        2) docker container prune -f ;;
        3) docker system prune -af ;;
        4) docker stats --no-stream ;;
        5) docker exec -it ${PROJECT_NAME} /bin/bash ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Function to show system information
show_system_info() {
    print_header
    print_color $BLUE "🔍 System Information"
    echo
    
    print_color $CYAN "🐳 Docker Version:"
    docker --version
    echo
    
    print_color $CYAN "📦 Docker Compose Version:"
    docker-compose --version
    echo
    
    print_color $CYAN "💾 System Resources:"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Disk: $(df -h . | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
    echo "CPU: $(nproc) cores"
    echo
    
    print_color $CYAN "🌐 Network:"
    ip addr show | grep inet | grep -v 127.0.0.1 | head -1
    echo
    
    read -p "Press Enter to continue..."
}

# Function for troubleshooting
troubleshooting() {
    print_header
    print_color $BLUE "🛠️ Troubleshooting"
    echo
    print_color $CYAN "1. Check bot connectivity"
    print_color $CYAN "2. Test database connection"
    print_color $CYAN "3. Verify environment variables"
    print_color $CYAN "4. Check port availability"
    print_color $CYAN "5. Container health check"
    echo
    read -p "Select option: " trouble_choice
    
    case $trouble_choice in
        1) docker exec ${PROJECT_NAME} python -c "import requests; print('Internet:', requests.get('https://api.telegram.org').status_code == 200)" ;;
        2) docker exec ${PROJECT_NAME} python -c "import sqlite3; sqlite3.connect('/app/data/bot_database.db').close(); print('Database: OK')" ;;
        3) docker exec ${PROJECT_NAME} env | grep -E "BOT_TOKEN|ADMIN_IDS" ;;
        4) netstat -tulpn | grep :8080 ;;
        5) docker inspect ${PROJECT_NAME} | grep -A 5 "Health" ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Main script execution
main() {
    # No root restriction - can run as any user
    
    while true; do
        show_main_menu
        case $choice in
            1) install_start_bot ;;
            2) stop_bot ;;
            3) restart_bot ;;
            4) show_status ;;
            5) show_logs ;;
            6) update_bot ;;
            7) configure_environment ;;
            8) uninstall_bot ;;
            9) container_management ;;
            10) show_system_info ;;
            11) troubleshooting ;;
            0) print_color $GREEN "👋 Goodbye!"; exit 0 ;;
            *) print_color $RED "❌ Invalid option! Please try again." ;;
        esac
    done
}

# Run main function
main "$@"
