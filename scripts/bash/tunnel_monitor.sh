#!/bin/bash

# Define terminal text formatting colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo "============================================================"
echo -e "🚀 ${CYAN}ZANNIE EXTERNAL TUNNEL GATEWAY INITIALIZER${NC}"
echo "============================================================"

# 1. Environment Dependency Scan
if ! command -v lt &> /dev/null; then
    echo -e "${YELLOW}[*] LocalTunnel package not found. Installing via npm natively...${NC}"
    npm install -g localtunnel
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Node/NPM ecosystem not configured on this container slot.${NC}"
        echo -e "Please run: apt update && apt install nodejs -y"
        exit 1
    fi
fi

echo -e "${GREEN}[+] Tunnel environment check passed successfully.${NC}"
echo "------------------------------------------------------------"
echo "[*] Initializing Reverse-Proxy Sockets..."

# 2. Boot Encrypted Tunnel for Frontend Web Server (Port 8080)
echo "[*] Generating public tunnel for Frontend UI (Port 8080)..."
nohup lt --port 8080 > sandbox_http_tunnel.log 2>&1 &

# 3. Boot Encrypted Tunnel for Flask API Endpoint (Port 5005)
echo "[*] Generating public tunnel for Backend API (Port 5005)..."
nohup lt --port 5005 > realestate_api_tunnel.log 2>&1 &

# Allow network handshakes to settle over the socket channels
sleep 4

echo "------------------------------------------------------------"
echo -e "📡 ${YELLOW}LIVE EXTERNAL ENDPOINT ROUTING TELEMETRY:${NC}"
echo "------------------------------------------------------------"

# 4. Extract generated URLs out of background system logs
if [ -f sandbox_http_tunnel.log ]; then
    FRONTEND_URL=$(grep -o 'https://[^ ]*' sandbox_http_tunnel.log | tail -n 1)
    echo -e "  ${GREEN}• Frontend UI Link :${NC} ${FRONTEND_URL:-'Establishing handshake... run cat sandbox_http_tunnel.log'}"
fi

if [ -f realestate_api_tunnel.log ]; then
    BACKEND_URL=$(grep -o 'https://[^ ]*' realestate_api_tunnel.log | tail -n 1)
    echo -e "  ${GREEN}• Backend API Link :${NC} ${BACKEND_URL:-'Establishing handshake... run cat realestate_api_tunnel.log'}"
fi
echo "============================================================"
echo -e "${CYAN}[INFO] Copy the Frontend link above to access your Hub from any device!${NC}"
echo "============================================================"

