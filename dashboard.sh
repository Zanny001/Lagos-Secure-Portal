#!/bin/bash

# Define terminal text formatting colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

check_process_status() {
    # Check if a process matching the pattern is running
    if pgrep -f "$1" > /dev/null; then
        echo -e "${GREEN}● RUNNING${NC}"
    else
        echo -e "${RED}○ STOPPED${NC}"
    fi
}

check_port_status() {
    # Lightweight, tool-agnostic socket check using built-in Python
    if python3 -c "import socket; s = socket.socket(); s.settimeout(0.2); exit(0 if s.connect_ex(('127.0.0.1', $1)) == 0 else 1)" 2>/dev/null; then
        echo -e "${GREEN}[Port $1: OPEN]${NC}"
    else
        echo -e "${RED}[Port $1: CLOSED]${NC}"
    fi
}

while true; do
    clear
    echo "============================================================"
    echo -e "🌐 ${CYAN}ZANNIE DIGITAL AUTOMATION SYSTEM — DEVOPS DASHBOARD${NC}"
    echo "============================================================"
    
    # Trace background processes
    echo -n "  Path A: Real Estate Crawler    --> "
    check_process_status "realestate_crawler.py"
    
    echo -n "  Path B: Crypto Volatility Bot  --> "
    check_process_status "crypto_threshold_engine.py"
    
    echo -n "  Path C: Real Estate Flask API  --> "
    check_process_status "realestate_api.py"
    check_port_status "5005"
    
    echo -n "  Path D: Frontend Web Server    --> "
    check_process_status "http.server 8080"
    check_port_status "8080"
    
    echo "============================================================"
    echo -e "🛠️  ${YELLOW}CONTROL PANEL MANAGEMENT ACTIONS:${NC}"
    echo "------------------------------------------------------------"
    echo "  [1] Start Real Estate Pipeline      [5] Kill Real Estate Crawler"
    echo "  [2] Start Crypto Volatility Bot     [6] Kill Crypto Volatility Bot"
    echo "  [3] Start Real Estate Flask API     [7] Kill Real Estate Flask API"
    echo "  [4] Start Frontend Web Server       [8] Kill Frontend Web Server"
    echo ""
    echo "  [A] Boot All Stack Infrastructure   [K] Kill All Environment Tasks"
    echo "  [Q] Exit Dashboard Terminal View"
    echo "============================================================"
    echo -n "Select Action Reference ID: "
    read -r choice

    case $choice in
        1)
            echo "[*] Launching Real Estate Lead Crawler..."
            nohup python3 -u realestate_crawler.py > logs/crawler.log 2>&1 &
            sleep 2
            ;;
        2)
            echo "[*] Launching Crypto Threshold Monitoring Engine..."
            nohup python3 -u crypto_threshold_engine.py > crypto_bot.log 2>&1 &
            sleep 2
            ;;
        3)
            echo "[*] Launching Real Estate API Core on Port 5005..."
            nohup python3 -u realestate_api.py > realestate_api.log 2>&1 &
            sleep 2
            ;;
        4)
            echo "[*] Spin-up Local Sandboxed HTTP Server on Port 8080..."
            nohup python3 -m http.server 8080 > sandbox_http.log 2>&1 &
            sleep 2
            ;;
        5)
            echo "[-] Disabling Real Estate Crawler..."
            pkill -f realestate_crawler.py
            sleep 1
            ;;
        6)
            echo "[-] Disabling Crypto Volatility Engine..."
            pkill -f crypto_threshold_engine.py
            sleep 1
            ;;
        7)
            echo "[-] Closing down API Instance on Port 5005..."
            pkill -f realestate_api.py
            sleep 1
            ;;
        8)
            echo "[-] Closing down Sandboxed Server on Port 8080..."
            pkill -f "http.server 8080"
            sleep 1
            ;;
        [Aa])
            echo "[*] Critical Booting Sequence Triggered..."
            nohup python3 -u realestate_api.py > realestate_api.log 2>&1 &
            nohup python3 -m http.server 8080 > sandbox_http.log 2>&1 &
            nohup python3 -u crypto_threshold_engine.py > crypto_bot.log 2>&1 &
            sleep 2
            ;;
        [Kk])
            echo "[!] Flushing All Background Tasks..."
            pkill -f realestate_crawler.py
            pkill -f crypto_threshold_engine.py
            pkill -f realestate_api.py
            pkill -f "http.server 8080"
            sleep 2
            ;;
        [Qq])
            clear
            echo "[*] Exiting DevOps Control Dashboard Session."
            break
            ;;
        *)
            echo -e "${RED}[!] Selection Invalid. Try again.${NC}"
            sleep 1
            ;;
    esac
done

