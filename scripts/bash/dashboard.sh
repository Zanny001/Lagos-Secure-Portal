#!/bin/bash

# ===================================================================
# DYNAMIC PATH DETERMINATION & ROOT ALIGNMENT
# ===================================================================
# Resolves the absolute directory of the bash script, then climbs up one tier to the root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Define terminal text formatting colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

check_process_status() {
    if pgrep -f "$1" > /dev/null; then
        echo -e "${GREEN}● RUNNING${NC}"
    else
        echo -e "${RED}○ STOPPED${NC}"
    fi
}

check_port_status() {
    if python3 -c "import socket; s = socket.socket(); s.settimeout(0.2); exit(0 if s.connect_ex(('127.0.0.1', $1)) == 0 else 1)" 2>/dev/null; then
        echo -e "${GREEN}[Port $1: OPEN]${NC}"
    else
        echo -e "${RED}[Port $1: CLOSED]${NC}"
    fi
}

check_file_status() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}● ONLINE (${2})${NC}"
    else
        echo -e "${RED}○ MISSING${NC}"
    fi
}

# Ensure logs subdirectory exists inside the root for smooth log streams
mkdir -p "$PROJECT_ROOT/logs"

while true; do
    clear
    echo "============================================================"
    echo -e "🌐 ${CYAN}ZANNIE DIGITAL AUTOMATION SYSTEM — DEVOPS DASHBOARD${NC}"
    echo "============================================================"

    # Trace background processes using explicit filenames
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

    echo -n "  Path E: Lagos Secure Verify    --> "
    check_process_status "node server.js"
    check_port_status "5000"

    echo -n "  Path F: Academic Stats Database -> "
    check_file_status "$PROJECT_ROOT/academic_records.db" "SQLite"

    echo "============================================================"
    echo -e "🛠️  ${YELLOW}CONTROL PANEL MANAGEMENT ACTIONS:${NC}"
    echo "------------------------------------------------------------"
    echo "  [1] Start Real Estate Crawler       [5] Kill Real Estate Crawler"
    echo "  [2] Start Crypto Volatility Bot     [6] Kill Crypto Volatility Bot"
    echo "  [3] Start Real Estate Flask API     [7] Kill Real Estate Flask API"
    echo "  [4] Start Frontend Web Server       [8] Kill Frontend Web Server"
    echo "  [9] Start Lagos Secure Verify       [10] Kill Lagos Secure Verify"
    echo "  ----------------------------------------------------------"
    echo "  [11] Launch Academic Grade Entry Loop (add_score.py)"
    echo "  [12] Force Recompile Analytics Markdown Report"
    echo "  [13] Run System Maintenance (Database Backup & Log Rotation)"
    echo ""
    echo "  [A] Boot All Stack Infrastructure   [K] Kill All Environment Tasks"
    echo "  [Q] Exit Dashboard Terminal View"
    echo "============================================================"
    echo -n "Select Action Reference ID: "
    read -r choice

    case $choice in
        1)
            echo "[*] Launching Real Estate Lead Crawler..."
            nohup python3 -u "$PROJECT_ROOT/scripts/scrapers/realestate_crawler.py" > "$PROJECT_ROOT/logs/crawler.log" 2>&1 &
            sleep 2
            ;;
        2)
            echo "[*] Launching Crypto Threshold Monitoring Engine..."
            nohup python3 -u "$PROJECT_ROOT/scripts/bots/crypto_threshold_engine.py" > "$PROJECT_ROOT/logs/crypto_bot.log" 2>&1 &
            sleep 2
            ;;
        3)
            echo "[*] Launching Real Estate API Core on Port 5005..."
            nohup python3 -u "$PROJECT_ROOT/scripts/scrapers/realestate_api.py" > "$PROJECT_ROOT/logs/realestate_api.log" 2>&1 &
            sleep 2
            ;;
        4)
            echo "[*] Spin-up Local Sandboxed HTTP Server on Port 8080..."
            cd "$PROJECT_ROOT" && nohup python3 -m http.server 8080 > "$PROJECT_ROOT/logs/sandbox_http.log" 2>&1 &
            sleep 2
            ;;
        9)
            echo "[*] Initializing Secure B2B Ingestion Node on Port 5000..."
            export PAYSTACK_SECRET_KEY="sk_test_your_secret_key_here"
            cd "$PROJECT_ROOT" && nohup node server.js > "$PROJECT_ROOT/logs/server.log" 2>&1 &
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
        10)
            echo "[-] Dismantling B2B API Server Node on Port 5000..."
            pkill -f "node server.js"
            sleep 1
            ;;
        11)
            echo "[*] Suspending control telemetry to open interactive grade logger..."
            sleep 1
            python3 "$PROJECT_ROOT/scripts/maintenance/add_score.py"
            echo -n "Press Enter to return to the control panel..."
            read -r
            ;;
        12)
            echo "[*] Regenerating student distribution performance matrices..."
            python3 "$PROJECT_ROOT/scripts/maintenance/compile_academic_stats.py"
            sleep 1.5
            ;;
        13)
            echo "[*] Executing full environment maintenance routine..."
            bash "$PROJECT_ROOT/scripts/bash/system_maintenance.sh"
            echo -n "Press Enter to return to the control panel..."
            read -r
            ;;
        [Aa])
            echo "[*] Pre-boot check: Securing state snapshot first..."
            bash "$PROJECT_ROOT/scripts/bash/system_maintenance.sh"
            echo "[*] Critical Booting Sequence Triggered... Spawning Cluster Matrix"
            nohup python3 -u "$PROJECT_ROOT/scripts/scrapers/realestate_api.py" > "$PROJECT_ROOT/logs/realestate_api.log" 2>&1 &
            cd "$PROJECT_ROOT" && nohup python3 -m http.server 8080 > "$PROJECT_ROOT/logs/sandbox_http.log" 2>&1 &
            nohup python3 -u "$PROJECT_ROOT/scripts/bots/crypto_threshold_engine.py" > "$PROJECT_ROOT/logs/crypto_bot.log" 2>&1 &
            export PAYSTACK_SECRET_KEY="sk_test_your_secret_key_here"
            cd "$PROJECT_ROOT" && nohup node server.js > "$PROJECT_ROOT/logs/server.log" 2>&1 &
            sleep 2
            ;;
        [Kk])
            echo "[!] Flushing All Background Tasks..."
            pkill -f realestate_crawler.py
            pkill -f crypto_threshold_engine.py
            pkill -f realestate_api.py
            pkill -f "http.server 8080"
            pkill -f "node server.js"
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
