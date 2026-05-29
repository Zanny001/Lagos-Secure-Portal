#!/bin/bash

# Configuration: Map system modules to their expected execution targets
SCRAPER_SCRIPT="run_scraper.py"
BOT_SCRIPT="crypto_signal_bot.py"
GATEWAY_SCRIPT="zannie_brand.py"
PHYSICS_SCRIPT="physics_app.py"

# Ports mapped to microservices
PORT_GATEWAY=5001
PORT_PHYSICS=5002

get_status() {
    local script_name=$1
    # Use head -n 1 to capture only the single most recent primary parent PID
    local p_id=$(pgrep -f "$script_name" | head -n 1)
    if [ -n "$p_id" ]; then
        echo -e "\e[32m● RUNNING\e[0m (PID: $p_id)"
    else
        echo -e "\e[31m○ STOPPED\e[0m"
    fi
}

check_port() {
    local port=$1
    if ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo -e "[\e[32mPort $port: OPEN\e[0m]"
    else
        echo -e "[\e[31mPort $port: CLOSED\e[0m]"
    fi
}

render_dashboard() {
    clear
    echo "============================================================"
    echo "🌐 ZANNIE DIGITAL AUTOMATION SYSTEM — DEVOPS DASHBOARD"
    echo "============================================================"
    echo -n "  Path A: Lead Harvester Core   --> "
    get_status "$SCRAPER_SCRIPT"
    
    echo -n "  Path B: RSI Crypto Bot Feed   --> "
    get_status "$BOT_SCRIPT"
    
    echo -n "  Path C: Paystack Gateway API  --> "
    get_status "$GATEWAY_SCRIPT"
    echo "                                    $(check_port $PORT_GATEWAY)"
    
    echo -n "  Path D: Physics Quiz Portal   --> "
    get_status "$PHYSICS_SCRIPT"
    echo "                                    $(check_port $PORT_PHYSICS)"
    echo "============================================================"
    echo "🛠️ CONTROL PANEL MANAGEMENT ACTIONS:"
    echo "------------------------------------------------------------"
    echo "  [1] Start Lead Harvester Engine     [5] Kill Lead Harvester"
    echo "  [2] Start RSI Crypto Monitor Feed   [6] Kill RSI Crypto Bot"
    echo "  [3] Start Paystack Gateway Server   [7] Kill Gateway Server"
    echo "  [4] Start Physics Evaluation App    [8] Kill Physics App"
    echo ""
    echo "  [A] Boot All Services Simultaneous   [K] Kill All Background Tasks"
    echo "  [Q] Exit Dashboard Terminal View"
    echo "============================================================"
}

# Defensive Start Pattern: Safely terminates older duplicates before binding ports
safe_start() {
    local script=$1
    local log_file=$2
    pkill -f "$script" 2>/dev/null
    sleep 0.2
    nohup python3 "$script" > "$log_file" 2>&1 &
}

manage_service() {
    case $1 in
        1) safe_start "$SCRAPER_SCRIPT" "scraper.log" ;;
        2) safe_start "$BOT_SCRIPT" "crypto.log" ;;
        3) safe_start "$GATEWAY_SCRIPT" "gateway.log" ;;
        4) safe_start "$PHYSICS_SCRIPT" "physics.log" ;;
        5) pkill -f "$SCRAPER_SCRIPT" ;;
        6) pkill -f "$BOT_SCRIPT" ;;
        7) pkill -f "$GATEWAY_SCRIPT" ;;
        8) pkill -f "$PHYSICS_SCRIPT" ;;
        A|a)
            safe_start "$SCRAPER_SCRIPT" "scraper.log"
            safe_start "$BOT_SCRIPT" "crypto.log"
            safe_start "$GATEWAY_SCRIPT" "gateway.log"
            safe_start "$PHYSICS_SCRIPT" "physics.log"
            ;;
        K|k)
            pkill -f "$SCRAPER_SCRIPT"
            pkill -f "$BOT_SCRIPT"
            pkill -f "$GATEWAY_SCRIPT"
            pkill -f "$PHYSICS_SCRIPT"
            ;;
        Q|q)
            exit 0
            ;;
        *)
            echo -e "\e[31mInvalid selection option.\e[0m"
            sleep 1
            ;;
    esac
}

# Main event execution loop
while true; do
    render_dashboard
    read -t 5 -n 1 -p "Select Action Reference ID: " ACTION
    if [ -n "$ACTION" ]; then
        manage_service "$ACTION"
    fi
done

