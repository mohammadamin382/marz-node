#!/bin/bash

# Colors for UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
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

# Function to generate random confirmation code
generate_confirmation_code() {
    echo "marz-node-$((RANDOM % 8901 + 100))"
}

# Function to check installation status
check_install_enabled() {
    if [ -f "$ENV_FILE" ]; then
        INSTALL_ENABLED=$(grep "^INSTALL_ENABLED=" "$ENV_FILE" | cut -d'=' -f2)
        if [ "$INSTALL_ENABLED" = "false" ]; then
            return 1
        fi
    else
        # Default to disabled if no .env file
        return 1
    fi
    return 0
}

# Function to show alpha warning
show_alpha_warning() {
    print_header
    print_color $RED "⚠️  ALPHA VERSION WARNING ⚠️"
    echo
    print_color $YELLOW "🔔 این ربات در حالت آلفا قرار دارد و هنوز آماده استفاده کامل نیست!"
    print_color $YELLOW "🐛 ممکن است باگ‌ها و مشکلات متعددی وجود داشته باشد"
    print_color $YELLOW "⚡ برای تست و توسعه طراحی شده است"
    echo
    print_color $PURPLE "📝 مشکلات احتمالی:"
    print_color $WHITE "   • مشکل در اتصال SSH"
    print_color $WHITE "   • خطاهای نصب نود"
    print_color $WHITE "   • عدم پایداری در اتصالات"
    print_color $WHITE "   • مدیریت خطای ناقص"
    echo
    print_color $CYAN "🎯 اگر مطمئن هستید که می‌خواهید ادامه دهید:"
    
    local confirmation_code=$(generate_confirmation_code)
    print_color $GREEN "   این کد را تایپ کنید: ${BOLD}$confirmation_code${NC}"
    echo
    
    read -p "$(print_color $WHITE "کد تأیید را وارد کنید: ")" user_input
    
    if [ "$user_input" = "$confirmation_code" ]; then
        print_color $GREEN "✅ تأیید شد! ادامه نصب..."
        sleep 2
        return 0
    else
        print_color $RED "❌ کد اشتباه است! خروج از برنامه..."
        exit 1
    fi
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

# Function to validate environment
validate_environment() {
    print_color $YELLOW "🔍 Validating environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        print_color $RED "❌ Environment file not found!"
        return 1
    fi
    
    BOT_TOKEN=$(grep "^BOT_TOKEN=" "$ENV_FILE" | cut -d'=' -f2)
    ADMIN_IDS=$(grep "^ADMIN_IDS=" "$ENV_FILE" | cut -d'=' -f2)
    
    if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
        print_color $RED "❌ Bot token not configured!"
        return 1
    fi
    
    if [ -z "$ADMIN_IDS" ] || [ "$ADMIN_IDS" = "123456789,987654321" ]; then
        print_color $RED "❌ Admin IDs not configured!"
        return 1
    fi
    
    print_color $GREEN "✅ Environment validation passed!"
    return 0
}

# Function to check system requirements
check_system_requirements() {
    print_color $YELLOW "🔍 Checking system requirements..."
    
    # Check available space
    available_space=$(df . | awk 'NR==2 {print $4}')
    required_space=1048576  # 1GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        print_color $RED "❌ Insufficient disk space! Required: 1GB, Available: $(($available_space/1024))MB"
        return 1
    fi
    
    # Check memory
    available_memory=$(free | awk '/^Mem:/ {print $7}')
    required_memory=524288  # 512MB in KB
    
    if [ "$available_memory" -lt "$required_memory" ]; then
        print_color $YELLOW "⚠️  Low memory detected. Bot may run slowly."
    fi
    
    # Check for required commands
    for cmd in curl git; do
        if ! command_exists $cmd; then
            print_color $YELLOW "📦 Installing $cmd..."
            apt-get update && apt-get install -y $cmd
        fi
    done
    
    print_color $GREEN "✅ System requirements check completed!"
    return 0
}

# Function to backup existing installation
backup_existing() {
    if [ -d "data" ] || [ -f "bot_database.db" ]; then
        print_color $YELLOW "📦 Creating backup of existing data..."
        backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        [ -d "data" ] && cp -r data "$backup_dir/"
        [ -f "bot_database.db" ] && cp bot_database.db "$backup_dir/"
        [ -f "$ENV_FILE" ] && cp "$ENV_FILE" "$backup_dir/"
        
        print_color $GREEN "✅ Backup created in $backup_dir"
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
    print_color $CYAN "12. 📋 Health Check"
    print_color $CYAN "13. 🔐 Security Audit"
    print_color $CYAN "14. 📊 Performance Monitor"
    print_color $CYAN "15. 💾 Backup & Restore"
    print_color $RED "0.  ❌ Exit"
    echo
    read -p "$(print_color $WHITE "Select an option: ")" choice
}

# Function to install and start bot
install_start_bot() {
    print_header
    print_color $BLUE "🚀 Installing and Starting Marzban Node Bot"
    echo
    
    # Check system requirements
    if ! check_system_requirements; then
        print_color $RED "❌ System requirements not met!"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    # Create backup
    backup_existing
    
    # Check dependencies
    install_docker
    install_docker_compose
    
    # Setup environment
    setup_environment
    
    # Validate environment
    if ! validate_environment; then
        print_color $RED "❌ Environment validation failed!"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    # Create data directory
    mkdir -p data logs
    chmod 755 data logs
    
    print_color $YELLOW "🔨 Building and starting bot..."
    
    # Build with progress
    docker-compose build --progress=plain
    
    if [ $? -ne 0 ]; then
        print_color $RED "❌ Failed to build bot!"
        read -p "Press Enter to continue..."
        return 1
    fi
    
    # Start services
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Bot installed and started successfully!"
        print_color $CYAN "🌐 Bot is now running in the background"
        
        # Wait and check health
        sleep 10
        health_check_silent
    else
        print_color $RED "❌ Failed to start bot!"
        print_color $YELLOW "📋 Checking logs for errors..."
        docker-compose logs --tail=20
    fi
    
    read -p "Press Enter to continue..."
}

# Function to stop bot
stop_bot() {
    print_header
    print_color $YELLOW "⏹️ Stopping bot..."
    docker-compose down
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Bot stopped successfully!"
    else
        print_color $RED "❌ Error stopping bot!"
    fi
    read -p "Press Enter to continue..."
}

# Function to restart bot
restart_bot() {
    print_header
    print_color $YELLOW "🔄 Restarting bot..."
    docker-compose restart
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Bot restarted successfully!"
        sleep 5
        health_check_silent
    else
        print_color $RED "❌ Error restarting bot!"
    fi
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
        echo
        
        # Show resource usage
        print_color $CYAN "📈 Resource Usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    else
        print_color $RED "❌ Bot is not running"
        echo
        print_color $YELLOW "📋 Last container status:"
        docker-compose ps -a
    fi
    
    echo
    read -p "Press Enter to continue..."
}

# Function to show logs with options
show_logs() {
    print_header
    print_color $BLUE "📋 Bot Logs"
    echo
    print_color $CYAN "1. Live logs (Ctrl+C to exit)"
    print_color $CYAN "2. Last 50 lines"
    print_color $CYAN "3. Last 100 lines"
    print_color $CYAN "4. Error logs only"
    print_color $CYAN "5. Search in logs"
    print_color $CYAN "6. Export logs to file"
    echo
    read -p "Select option: " log_choice
    
    case $log_choice in
        1) 
            print_color $YELLOW "Showing live logs (Press Ctrl+C to exit)..."
            docker-compose logs -f 
            ;;
        2) docker-compose logs --tail=50 ;;
        3) docker-compose logs --tail=100 ;;
        4) 
            print_color $YELLOW "Filtering error logs..."
            docker-compose logs | grep -i "error\|exception\|failed"
            ;;
        5)
            read -p "Enter search term: " search_term
            docker-compose logs | grep -i "$search_term"
            ;;
        6)
            log_file="bot_logs_$(date +%Y%m%d_%H%M%S).txt"
            docker-compose logs > "$log_file"
            print_color $GREEN "✅ Logs exported to $log_file"
            ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
}

# Function to update bot
update_bot() {
    print_header
    print_color $YELLOW "🔧 Updating bot..."
    
    # Create backup before update
    backup_existing
    
    # Check if git repository
    if [ -d ".git" ]; then
        print_color $YELLOW "📥 Pulling latest changes..."
        git pull origin main
        
        if [ $? -ne 0 ]; then
            print_color $RED "❌ Failed to pull updates!"
            read -p "Press Enter to continue..."
            return 1
        fi
    else
        print_color $YELLOW "⚠️  Not a git repository. Manual update required."
    fi
    
    # Rebuild and restart
    print_color $YELLOW "🔨 Rebuilding bot..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Bot updated successfully!"
        sleep 5
        health_check_silent
    else
        print_color $RED "❌ Update failed!"
    fi
    
    read -p "Press Enter to continue..."
}

# Function to configure environment with advanced options
configure_environment() {
    print_header
    print_color $BLUE "⚙️ Environment Configuration"
    echo
    
    if [ -f "$ENV_FILE" ]; then
        print_color $CYAN "Current configuration:"
        cat "$ENV_FILE" | grep -v "^#" | grep -v "^$" | while read line; do
            key=$(echo $line | cut -d'=' -f1)
            value=$(echo $line | cut -d'=' -f2)
            if [[ $key == *"TOKEN"* ]] || [[ $key == *"PASSWORD"* ]]; then
                echo "$key=***hidden***"
            else
                echo "$line"
            fi
        done
        echo
    fi
    
    print_color $YELLOW "1. Edit configuration file"
    print_color $YELLOW "2. Reset to default"
    print_color $YELLOW "3. Show current config"
    print_color $YELLOW "4. Validate configuration"
    print_color $YELLOW "5. Enable installation mode"
    print_color $YELLOW "6. Disable installation mode"
    echo
    read -p "Select option: " config_choice
    
    case $config_choice in
        1) 
            if command_exists nano; then
                nano "$ENV_FILE"
            elif command_exists vi; then
                vi "$ENV_FILE"
            else
                print_color $RED "No text editor available!"
            fi
            ;;
        2) 
            cp .env.example "$ENV_FILE" 
            setup_environment
            ;;
        3) 
            cat "$ENV_FILE" 
            ;;
        4)
            validate_environment
            ;;
        5)
            sed -i 's/INSTALL_ENABLED=false/INSTALL_ENABLED=true/' "$ENV_FILE"
            print_color $GREEN "✅ Installation mode enabled!"
            ;;
        6)
            sed -i 's/INSTALL_ENABLED=true/INSTALL_ENABLED=false/' "$ENV_FILE"
            print_color $GREEN "✅ Installation mode disabled!"
            ;;
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
        # Create final backup
        backup_existing
        
        print_color $YELLOW "Stopping and removing containers..."
        docker-compose down -v
        
        print_color $YELLOW "Removing images..."
        docker rmi $(docker images "*$PROJECT_NAME*" -q) 2>/dev/null
        
        print_color $YELLOW "Cleaning up..."
        docker system prune -f
        
        # Remove data directories
        read -p "Remove data directories? (y/N): " remove_data
        if [[ $remove_data =~ ^[Yy]$ ]]; then
            rm -rf data logs
            print_color $YELLOW "Data directories removed"
        fi
        
        print_color $GREEN "✅ Bot uninstalled successfully!"
    else
        print_color $CYAN "Operation cancelled."
    fi
    
    read -p "Press Enter to continue..."
}

# Function for advanced container management
container_management() {
    print_header
    print_color $BLUE "📦 Container Management"
    echo
    print_color $CYAN "1. List all containers"
    print_color $CYAN "2. Remove unused containers"
    print_color $CYAN "3. Clean up system"
    print_color $CYAN "4. Container resource usage"
    print_color $CYAN "5. Exec into container"
    print_color $CYAN "6. Container logs"
    print_color $CYAN "7. Inspect container"
    print_color $CYAN "8. Container network info"
    echo
    read -p "Select option: " container_choice
    
    case $container_choice in
        1) 
            docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"
            ;;
        2) 
            docker container prune -f
            print_color $GREEN "✅ Unused containers removed"
            ;;
        3) 
            docker system prune -af
            print_color $GREEN "✅ System cleaned up"
            ;;
        4) 
            docker stats --no-stream
            ;;
        5) 
            if docker ps | grep -q "$PROJECT_NAME"; then
                docker exec -it $(docker ps --filter "name=$PROJECT_NAME" --format "{{.Names}}" | head -1) /bin/bash
            else
                print_color $RED "❌ No running container found!"
            fi
            ;;
        6)
            docker logs $(docker ps --filter "name=$PROJECT_NAME" --format "{{.Names}}" | head -1)
            ;;
        7)
            docker inspect $(docker ps --filter "name=$PROJECT_NAME" --format "{{.Names}}" | head -1)
            ;;
        8)
            docker network ls
            echo
            docker inspect $(docker ps --filter "name=$PROJECT_NAME" --format "{{.Names}}" | head -1) | grep -A 10 "Networks"
            ;;
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
    echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
    echo
    
    print_color $CYAN "🌐 Network:"
    ip addr show | grep inet | grep -v 127.0.0.1 | head -1
    echo
    
    print_color $CYAN "🔧 Container Info:"
    if docker ps | grep -q "$PROJECT_NAME"; then
        docker inspect $(docker ps --filter "name=$PROJECT_NAME" --format "{{.Names}}" | head -1) | grep -E "\"IPAddress\"|\"Gateway\"|\"Created\""
    else
        echo "No containers running"
    fi
    
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
    print_color $CYAN "6. Network diagnostics"
    print_color $CYAN "7. Permission check"
    print_color $CYAN "8. Disk space analysis"
    echo
    read -p "Select option: " trouble_choice
    
    case $trouble_choice in
        1) 
            print_color $YELLOW "Testing internet connectivity..."
            if curl -s --max-time 10 https://api.telegram.org > /dev/null; then
                print_color $GREEN "✅ Internet connection: OK"
            else
                print_color $RED "❌ Internet connection: Failed"
            fi
            ;;
        2) 
            print_color $YELLOW "Testing database connection..."
            if [ -f "data/bot_database.db" ]; then
                print_color $GREEN "✅ Database file exists"
            else
                print_color $RED "❌ Database file not found"
            fi
            ;;
        3) 
            print_color $YELLOW "Checking environment variables..."
            validate_environment
            ;;
        4) 
            print_color $YELLOW "Checking port availability..."
            netstat -tulpn | grep :8080 || echo "Port 8080 is available"
            ;;
        5) 
            print_color $YELLOW "Checking container health..."
            health_check_silent
            ;;
        6)
            print_color $YELLOW "Running network diagnostics..."
            ping -c 3 google.com
            ;;
        7)
            print_color $YELLOW "Checking permissions..."
            ls -la data/ logs/ 2>/dev/null || echo "Directories not found"
            ;;
        8)
            print_color $YELLOW "Analyzing disk space..."
            df -h
            echo
            du -sh data/ logs/ 2>/dev/null || echo "No data directories found"
            ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Function for health check
health_check() {
    print_header
    print_color $BLUE "📋 Health Check"
    echo
    
    health_check_silent
    
    read -p "Press Enter to continue..."
}

# Silent health check function
health_check_silent() {
    local health_score=0
    local total_checks=5
    
    print_color $YELLOW "🔍 Running health checks..."
    echo
    
    # Check 1: Container status
    if docker-compose ps | grep -q "Up"; then
        print_color $GREEN "✅ Container Status: Running"
        ((health_score++))
    else
        print_color $RED "❌ Container Status: Not running"
    fi
    
    # Check 2: Environment file
    if [ -f "$ENV_FILE" ] && validate_environment > /dev/null 2>&1; then
        print_color $GREEN "✅ Environment: Configured"
        ((health_score++))
    else
        print_color $RED "❌ Environment: Not configured"
    fi
    
    # Check 3: Database
    if [ -f "data/bot_database.db" ]; then
        print_color $GREEN "✅ Database: Available"
        ((health_score++))
    else
        print_color $RED "❌ Database: Not found"
    fi
    
    # Check 4: Internet connectivity
    if curl -s --max-time 5 https://api.telegram.org > /dev/null; then
        print_color $GREEN "✅ Connectivity: Online"
        ((health_score++))
    else
        print_color $RED "❌ Connectivity: Offline"
    fi
    
    # Check 5: Resource usage
    memory_usage=$(docker stats --no-stream --format "{{.MemPerc}}" 2>/dev/null | head -1 | sed 's/%//')
    if [ -n "$memory_usage" ] && [ "${memory_usage%.*}" -lt 80 ]; then
        print_color $GREEN "✅ Resources: Normal usage"
        ((health_score++))
    else
        print_color $YELLOW "⚠️  Resources: High usage or unavailable"
    fi
    
    echo
    print_color $CYAN "🏥 Health Score: $health_score/$total_checks"
    
    if [ $health_score -eq $total_checks ]; then
        print_color $GREEN "🎉 Perfect health!"
    elif [ $health_score -ge 3 ]; then
        print_color $YELLOW "⚠️  Fair health - some issues detected"
    else
        print_color $RED "❌ Poor health - multiple issues detected"
    fi
}

# Function for security audit
security_audit() {
    print_header
    print_color $BLUE "🔐 Security Audit"
    echo
    
    print_color $YELLOW "🔍 Running security checks..."
    echo
    
    # Check file permissions
    print_color $CYAN "📁 File Permissions:"
    if [ -f "$ENV_FILE" ]; then
        perm=$(stat -c "%a" "$ENV_FILE")
        if [ "$perm" = "600" ] || [ "$perm" = "644" ]; then
            print_color $GREEN "✅ Environment file permissions: Secure ($perm)"
        else
            print_color $YELLOW "⚠️  Environment file permissions: $perm (consider 600)"
        fi
    fi
    
    # Check for exposed ports
    print_color $CYAN "🌐 Network Security:"
    exposed_ports=$(netstat -tulpn | grep LISTEN | wc -l)
    print_color $WHITE "   Open ports: $exposed_ports"
    
    # Check Docker security
    print_color $CYAN "🐳 Docker Security:"
    if docker info 2>/dev/null | grep -q "Security Options"; then
        print_color $GREEN "✅ Docker security features enabled"
    else
        print_color $YELLOW "⚠️  Basic Docker security"
    fi
    
    # Check for default credentials
    print_color $CYAN "🔑 Credential Security:"
    if grep -q "your_telegram_bot_token_here" "$ENV_FILE" 2>/dev/null; then
        print_color $RED "❌ Default bot token detected!"
    else
        print_color $GREEN "✅ Bot token configured"
    fi
    
    read -p "Press Enter to continue..."
}

# Function for performance monitoring
performance_monitor() {
    print_header
    print_color $BLUE "📊 Performance Monitor"
    echo
    
    if ! docker ps | grep -q "$PROJECT_NAME"; then
        print_color $RED "❌ Bot is not running!"
        read -p "Press Enter to continue..."
        return
    fi
    
    print_color $YELLOW "📈 Real-time Performance (Press Ctrl+C to exit):"
    echo
    
    # Show real-time stats
    docker stats $(docker ps --filter "name=$PROJECT_NAME" --format "{{.Names}}")
}

# Function for backup and restore
backup_restore() {
    print_header
    print_color $BLUE "💾 Backup & Restore"
    echo
    print_color $CYAN "1. Create backup"
    print_color $CYAN "2. List backups"
    print_color $CYAN "3. Restore from backup"
    print_color $CYAN "4. Delete old backups"
    print_color $CYAN "5. Auto backup setup"
    echo
    read -p "Select option: " backup_choice
    
    case $backup_choice in
        1)
            backup_existing
            ;;
        2)
            print_color $CYAN "📋 Available backups:"
            ls -la backup_* 2>/dev/null || print_color $YELLOW "No backups found"
            ;;
        3)
            print_color $CYAN "📋 Available backups:"
            ls -d backup_* 2>/dev/null || { print_color $YELLOW "No backups found"; read -p "Press Enter to continue..."; return; }
            echo
            read -p "Enter backup directory name: " backup_dir
            if [ -d "$backup_dir" ]; then
                print_color $YELLOW "Restoring from $backup_dir..."
                docker-compose down
                [ -f "$backup_dir/$ENV_FILE" ] && cp "$backup_dir/$ENV_FILE" .
                [ -d "$backup_dir/data" ] && cp -r "$backup_dir/data" .
                docker-compose up -d
                print_color $GREEN "✅ Restore completed!"
            else
                print_color $RED "❌ Backup directory not found!"
            fi
            ;;
        4)
            print_color $YELLOW "🗑️ Deleting backups older than 7 days..."
            find . -name "backup_*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null
            print_color $GREEN "✅ Old backups cleaned up"
            ;;
        5)
            print_color $YELLOW "⚙️ Auto backup setup not implemented yet"
            ;;
        *) print_color $RED "Invalid option!" ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Main script execution
main() {
    # Check if installation is enabled
    if ! check_install_enabled; then
        show_alpha_warning
    fi
    
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
            12) health_check ;;
            13) security_audit ;;
            14) performance_monitor ;;
            15) backup_restore ;;
            0) print_color $GREEN "👋 Goodbye!"; exit 0 ;;
            *) 
                print_color $RED "❌ Invalid option! Please try again."
                sleep 2
                ;;
        esac
    done
}

# Run main function
main "$@"
