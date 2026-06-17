#!/bin/bash

# ==================================================================
#                 ZANNIE INFRASTRUCTURE WATCHDOG
#               AUTOMATED DAEMON RECOVERY ENGINE
# ==================================================================
# Monitor Interval: 60 Seconds

echo "Initializing Zannie Infrastructure Watchdog..."
echo "Monitoring target arrays: Flask (5005), Crypto Ticker, & HTTP Sandbox (8080)"
echo "------------------------------------------------------------------"

while true; do
    # 1. VERIFY FLASK API WORKER NODE
    if ! pgrep -f "realestate_api.py" > /dev/null; then
        echo "[ALERT] $(date '+%Y-%m-%d %H:%M:%S') - Flask API Core is offline! Recovering..."
        nohup python3 -u realestate_api.py > realestate_api.log 2>&1 &
    fi

    # 2. VERIFY CRYPTO VOLATILITY MONITOR DAEMON
    if ! pgrep -f "crypto_threshold_engine.py" > /dev/null; then
        echo "[ALERT] $(date '+%Y-%m-%d %H:%M:%S') - Crypto Ticker Engine is offline! Recovering..."
        nohup python3 -u crypto_threshold_engine.py > crypto_alert_bot.log 2>&1 &
    fi

    # 3. VERIFY LOCAL HTTP SANDBOX SERVER (PORT 8080)
    # Checks if the http.server module is missing from the active background list
    if ! pgrep -f "http.server 8080" > /dev/null; then
        echo "[ALERT] $(date '+%Y-%m-%d %H:%M:%S') - Local HTTP Server on 8080 is offline! Recovering..."
        nohup python3 -m http.server 8080 > sandbox_http.log 2>&1 &
        echo "[RECOVERY] HTTP Sandbox Server rebooted successfully on Port 8080."
    fi

    sleep 60
done

