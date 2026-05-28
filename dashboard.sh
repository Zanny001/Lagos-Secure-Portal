#!/bin/bash

# Configuration: Map system modules to their expected execution files
SCRAPER_SCRIPT="run_scraper.py"
BOT_SCRIPT="crypto_signal_bot.py"
GATEWAY_SCRIPT="zannie_brand.py"
PHYSICS_SCRIPT="physics_app.py"

get_status() {
    local script_name=$1
    local p_id=$(pgrep -f "$script_name")
    if [ -n "$p_id" ]; then
        echo -e "\e[32m● RUNNING\e[0m (PID: $p_id)"
    else
        echo -e "\e[31m○ STOPPED\e[0m"
    fi
}

check_port() {
    local port=$1
    if command -v ss &> /dev/null; then
        ss -tulpn | grep -q ":$port " && echo -e " [Port $port: \e[32mBOUND\e[0m]" || echo -e " [Port $port: \e[33mOPEN\e[0m]"
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$port " && echo -e " [Port $port: \e[32mBOUND\e[0m]" || echo -e " [Port $port: \e[33mOPEN\e[0m]"
    else
        echo ""
    fi
}

while true; do
    clear
    echo "============================================================"
    echo "🌐 ZANNIE DIGITAL AUTOMATION SYSTEM — DEVOPS DASHBOARD"
    echo "============================================================"
    echo -e "Path A: Lead Harvester Core   --> $(get_status $SCRAPER_SCRIPT)"
    echo -e "Path B: RSI Crypto Bot Feed   --> $(get_status $BOT_SCRIPT)"
    echo -e "Path C: Paystack Gateway API  --> $(get_status $GATEWAY_SCRIPT)$(check_port 5001)"
    echo -e "Path D: Physics Quiz Portal   --> $(get_status $PHYSICS_SCRIPT)$(check_port 5002)"
    echo "============================================================"
    echo "🛠️ CONTROL PANEL MANAGEMENT ACTIONS:"
    echo "------------------------------------------------------------"
    echo "  [1] Start Lead Harvester Engine     [5] Kill Lead Harvester"
    echo "  [2] Start RSI Crypto Monitor Feed   [6] Kill RSI Crypto Bot"
    echo "  [3] Start Paystack Gateway Server   [7] Kill Gateway Server"
    echo "  [4] Start Physics Evaluation App    [8] Kill Physics App"
    echo "  [A] Boot All Services Simultaneous   [K] Kill All Background Tasks"
    echo "  [Q] Exit Dashboard Terminal View"
    echo "------------------------------------------------------------"
    read -p "Select control action index target: " choice

    case $choice in
        1) nohup python3 $SCRAPER_SCRIPT > scraper.log 2>&1 & sleep 1 ;;
        2) nohup python3 $BOT_SCRIPT > crypto.log 2>&1 & sleep 1 ;;
        3) nohup python3 $GATEWAY_SCRIPT > gateway.log 2>&1 & sleep 1 ;;
        4) nohup python3 $PHYSICS_SCRIPT > physics.log 2>&1 & sleep 1 ;;
        
        5) pkill -f $SCRAPER_SCRIPT ;;
        6) pkill -f $BOT_SCRIPT ;;
        7) pkill -f $GATEWAY_SCRIPT ;;
        8) pkill -f $PHYSICS_SCRIPT ;;
        
        [Aa])
            nohup python3 $SCRAPER_SCRIPT > scraper.log 2>&1 &
            nohup python3 $BOT_SCRIPT > crypto.log 2>&1 &
            nohup python3 $GATEWAY_SCRIPT > gateway.log 2>&1 &
            nohup python3 $PHYSICS_SCRIPT > physics.log 2>&1 &
            sleep 1
            ;;
        [Kk])
            pkill -f $SCRAPER_SCRIPT
            pkill -f $BOT_SCRIPT
            pkill -f $GATEWAY_SCRIPT
            pkill -f $PHYSICS_SCRIPT
            sleep 1
            ;;
        [Qq])
            clear
            echo "Exited dashboard interface loop context safely."
            break
            ;;
        *)
            echo -e "\e[31mInvalid action target selected.\e[0m" && sleep 1
            ;;
    esac
done
