#!/bin/bash

echo "====================================================="
echo "   ZANNIE MULTI-NODE INFRASTRUCTURE BOOT SEQUENCE    "
echo "====================================================="

# 1. Dynamic Path Resolution — Pivot out to project root folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# 2. Clear any lingering processes on Port 5001
echo "[+] Scanning for stale socket connections on Port 5001..."
# Using lsof or netstat safely within the environment
PID=$(lsof -t -i:5001 2>/dev/null || sudo netstat -nlp 2>/dev/null | grep :5001 | awk '{print $7}' | cut -d'/' -f1)

if [ -n "$PID" ]; then
    echo "[-] Port conflict detected (PID: $PID). Terminating..."
    kill -9 $PID 2>/dev/null || sudo kill -9 $PID
    echo "[+] Port 5001 successfully cleared."
else
    echo "[+] Port 5001 is clear."
fi

# 3. Verify Database Presence in the Absolute Root Destination
echo "[+] Verifying SQLite clusters at: $PROJECT_ROOT"
if [ -f "academic_records.db" ] && [ -f "zannie_sales.db" ]; then
    echo "[+] Storage clusters validated."
else
    echo "[!] Warning: Storage clusters not found. Engine will initialize new schemas."
fi

# 4. Launch the Core Engine from the Correct Environment Target
echo "[+] Booting Application Server via local Virtual Environment..."
echo "====================================================="

if [ -f "venv/bin/python" ]; then
    # Executes seamlessly within your isolated workspace parameters
    ./venv/bin/python app.py
else
    python3 app.py
fi
