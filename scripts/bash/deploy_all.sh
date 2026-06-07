#!/bin/bash

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
PID_FILE="./services.pid"

start_services() {
    echo "=========================================================="
    echo "🚀 LAUNCHING ALL PORTFOLIO BACKGROUND SERVICES..."
    echo "=========================================================="

    # 1. Zannie Payment Gateway Router (Port 5001)
    if [ -f "zannie_brand.py" ]; then
        echo "[DEPLOY] Starting Payment Gateway Engine (Port 5001)..."
        nohup python zannie_brand.py > "$LOG_DIR/zannie_gateway.log" 2>&1 &
    fi

    # 2. Real-Time RAM RSI Bot Engine
    if [ -f "crypto_signal_bot.py" ]; then
        echo "[DEPLOY] Starting RAM RSI Market Tracker Bot..."
        nohup python crypto_signal_bot.py > "$LOG_DIR/crypto_bot.log" 2>&1 &
    fi

    # 3. Physics Assessment Matrix UI (Port 5002)
    if [ -f "physics_app.py" ]; then
        echo "[DEPLOY] Starting Academic Scoring Portal (Port 5002)..."
        nohup python physics_app.py > "$LOG_DIR/physics_portal.log" 2>&1 &
    fi

    # 4. Infrastructure Heartbeat Watchdog Deamon
    if [ -f "sys_watchdog.py" ]; then
        echo "[DEPLOY] Starting Automated Port Watchdog Monitor..."
        nohup python sys_watchdog.py > "$LOG_DIR/sys_watchdog.log" 2>&1 &
    fi

    # 5. Asynchronous Sports Live Ticker Engine
    if [ -f "sports_ticker.py" ]; then
        echo "[DEPLOY] Starting Live Sports Data Ticker Process..."
        nohup python sports_ticker.py > "$LOG_DIR/sports_ticker.log" 2>&1 &
    fi

    # 6. Automated Status Summary Broadcast Daemon <-- Added
    if [ -f "sys_reporter.py" ]; then
        echo "[DEPLOY] Starting Automated Status Broadcast Reporter..."
        nohup python sys_reporter.py > "$LOG_DIR/sys_reporter.log" 2>&1 &
    fi

    echo "----------------------------------------------------------"
    echo "✅ DEPLOYMENT SYSTEM STATUS: ONLINE"
    echo "👉 Manage services globally via: zannie status"
    echo "=========================================================="
}

stop_services() {
    echo "=========================================================="
    echo "🛑 TERMINATING ALL BACKGROUND PORTFOLIO RUNTIMES..."
    echo "=========================================================="
    
    if [ -f "db_maintenance.py" ]; then
        python db_maintenance.py
    fi
    
    pkill -f "python zannie_brand.py"
    pkill -f "python crypto_signal_bot.py"
    pkill -f "python physics_app.py"
    pkill -f "python sys_watchdog.py"
    pkill -f "python sports_ticker.py"
    pkill -f "python sys_reporter.py"  # <-- Terminate reporting loop cleanly
    
    [ -f "$PID_FILE" ] && rm "$PID_FILE"
    echo "✅ STATUS: CLEAN DISCONNECT. Environment blocks recycled safely."
    echo "=========================================================="
}

status_services() {
    echo "=========================================================="
    echo "📊 SYSTEM INTEGRITY COMPONENT STATUS REPORT"
    echo "=========================================================="
    
    GATEWAY_PID=$(pgrep -f "python zannie_brand.py")
    BOT_PID=$(pgrep -f "python crypto_signal_bot.py")
    PHYSICS_PID=$(pgrep -f "python physics_app.py")
    WATCHDOG_PID=$(pgrep -f "python sys_watchdog.py")
    SPORTS_PID=$(pgrep -f "python sports_ticker.py")
    REPORTER_PID=$(pgrep -f "python sys_reporter.py") # <-- Track reporter process

    [ -n "$GATEWAY_PID" ] && echo "🟢 [ONLINE] zannie_brand.py       -> PID: $GATEWAY_PID (Port 5001)" || echo "🔴 [OFFLINE] zannie_brand.py      -> Offline"
    [ -n "$BOT_PID" ] && echo "🟢 [ONLINE] crypto_signal_bot.py  -> PID: $BOT_PID (RAM Mode)" || echo "🔴 [OFFLINE] crypto_signal_bot.py -> Offline"
    [ -n "$PHYSICS_PID" ] && echo "🟢 [ONLINE] physics_app.py        -> PID: $PHYSICS_PID (Port 5002)" || echo "🔴 [OFFLINE] physics_app.py       -> Offline"
    [ -n "$WATCHDOG_PID" ] && echo "🟢 [ONLINE] sys_watchdog.py       -> PID: $WATCHDOG_PID (Monitor)" || echo "🔴 [OFFLINE] sys_watchdog.py      -> Offline"
    [ -n "$SPORTS_PID" ]   && echo "🟢 [ONLINE] sports_ticker.py      -> PID: $SPORTS_PID (Live Odds)" || echo "🔴 [OFFLINE] sports_ticker.py     -> Offline"
    [ -n "$REPORTER_PID" ] && echo "🟢 [ONLINE] sys_reporter.py       -> PID: $REPORTER_PID (Broadcast)" || echo "🔴 [OFFLINE] sys_reporter.py      -> Offline"
    echo "=========================================================="
}

case "$1" in
    start) start_services ;;
    stop) stop_services ;;
    status) status_services ;;
    *)
        echo "Usage: zannie {start|stop|status}"
        exit 1
esac

