#!/bin/bash

# ==================================================================
#                 ZANNIE INFRASTRUCTURE WATCHDOG
#               AUTOMATED DAEMON RECOVERY ENGINE
# ==================================================================
# Monitor Interval: 60 Seconds

echo "Initializing Zannie Infrastructure Watchdog..."
echo "Monitoring target arrays: Flask Web API (Port 5005) & Crypto Ticker Engine"
echo "------------------------------------------------------------------"

while true; do
    # 1. VERIFY FLASK API WORKER NODE
    # Check if the process 'realestate_api.py' is currently present in the process tree
    if ! pgrep -f "realestate_api.py" > /dev/null; then
        echo "[ALERT] $(date '+%Y-%m-%d %H:%M:%S') - Flask API Core is offline! Initializing recovery..."
        nohup python3 -u realestate_api.py > realestate_api.log 2>&1 &
        echo "[RECOVERY] Flask API microservice rebooted successfully on Port 5005."
    fi

    # 2. VERIFY CRYPTO VOLATILITY MONITOR DAEMON
    # Check if the process 'crypto_threshold_engine.py' is active
    if ! pgrep -f "crypto_threshold_engine.py" > /dev/null; then
        echo "[ALERT] $(date '+%Y-%m-%d %H:%M:%S') - Crypto Ticker Engine is offline! Initializing recovery..."
        nohup python3 -u crypto_threshold_engine.py > crypto_alert_bot.log 2>&1 &
        echo "[RECOVERY] Crypto Volatility Monitor daemon rebooted successfully."
    fi

    # Pause execution for 60 seconds before cycling the telemetry check
    sleep 60
done

