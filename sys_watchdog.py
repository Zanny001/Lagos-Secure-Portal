import socket
import time
import requests

# Monitoring Targets Configuration Matrix
MONITOR_PORTS = {
    5001: "Zannie Payment Gateway Engine",
    5002: "Academic Scoring Portal Engine"
}
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/mock_crypto_channel_token"

def check_port_status(port):
    """Attempts to establish a local connection to verify a port is active."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        result = s.connect_ex(('127.0.0.1', port))
        return result == 0  # Returns True if port connection succeeds cleanly

def dispatch_status_alert(service_name, port, is_online):
    """Sends a formatted status update embed directly to your Discord monitor channel."""
    if is_online:
        payload = {
            "embeds": [{
                "title": f"🟢 SERVICE RECOVERED: {service_name}",
                "color": 3066993,  # Emerald Green
                "description": f"The microservice on **Port {port}** is responsive and processing traffic cleanly.",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }]
        }
    else:
        payload = {
            "embeds": [{
                "title": f"🚨 SERVICE ALERT: {service_name} IS OFFLINE",
                "color": 15158332,  # Crimson Red
                "description": f"The background application on **Port {port}** is unresponsive.\nAction required: Restart workspace using `zannie start`.",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }]
        }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"[WATCHDOG ERROR] Failed to dispatch alert: {e}")

def run_watchdog_loop():
    print("==========================================================")
    print("🛰️ INFRASTRUCTURE HEARTBEAT WATCHDOG DEAMON ACTIVE")
    print("==========================================================")
    
    # Track previous state configurations to prevent spamming your Discord feed
    last_known_state = {port: True for port in MONITOR_PORTS}

    while True:
        for port, service_name in MONITOR_PORTS.items():
            current_state = check_port_status(port)
            
            # If state shifts (e.g., app drops offline or boots back up), trigger notification
            if current_state != last_known_state[port]:
                dispatch_status_alert(service_name, port, current_state)
                last_known_state[port] = current_state
                
        # Scans local ports every 60 seconds (adjust to a longer interval for production use)
        time.sleep(60)

if __name__ == "__main__":
    run_watchdog_loop()

