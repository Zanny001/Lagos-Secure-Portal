import http.client
import json
import os
import subprocess
import sys

# Color configurations for clear local terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

LOCAL_HOST = "127.0.0.1"
PORT = 5005

# ==============================================================================
# DISCORD NOTIFICATION CONFIGURATION
# ==============================================================================
# Paste your active Zannie Discord Channel Webhook URL here
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

def dispatch_discord_alert(title, description, color_code, status_fields):
    """
    Formulates and dispatches a structured rich embed payload alert
    directly to your Discord channel via the webhook link.
    """
    if not DISCORD_WEBHOOK_URL or "YOUR_DISCORD_WEBHOOK" in DISCORD_WEBHOOK_URL:
        print("[!] Discord Alert skipped: Webhook URL unconfigured.")
        return

    # Split webhook URL into host and path components safely
    try:
        url_clean = DISCORD_WEBHOOK_URL.replace("https://", "")
        parts = url_clean.split("/", 1)
        host = parts[0]
        path = "/" + parts[1]
    except Exception as e:
        print(f"[-] Failed to parse Discord Webhook URL: {e}")
        return

    payload = {
        "username": "Zannie Core Watchdog",
        "avatar_url": "https://i.imgur.com/w8N93Zf.png",  # Clean tech avatar
        "embeds": [{
            "title": title,
            "description": description,
            "color": color_code,  # Decimal color representation
            "fields": status_fields,
            "footer": {
                "text": "Automated Telemetry Node Daemon Monitor"
            }
        }]
    }

    try:
        json_data = json.dumps(payload)
        headers = {"Content-Type": "application/json"}
        conn = http.client.HTTPSConnection(host)
        conn.request("POST", path, body=json_data, headers=headers)
        response = conn.getresponse()
        conn.close()

        if response.status in [200, 204]:
            print("[+] Diagnostic alert pushed successfully to Discord channel.")
        else:
            print(f"[-] Discord API returned non-OK status: {response.status}")
    except Exception as e:
        print(f"[-] Webhook push execution breakdown: {e}")

def check_local_endpoint(path):
    """Pings an internal server endpoint path and evaluates its response status."""
    try:
        conn = http.client.HTTPConnection(LOCAL_HOST, PORT, timeout=3)
        conn.request("GET", path)
        response = conn.getresponse()
        status = response.status
        data = response.read().decode('utf-8')
        conn.close()
        return status, data
    except Exception:
        return None, None

def inspect_active_processes():
    """Scans the system process tree to see if the core Flask API engine is running."""
    try:
        output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
        return "realestate_api.py" in output
    except Exception:
        return False

def run_system_diagnostic():
    print(f"\n{BOLD}=== ZANNIE HUB SYSTEM HEALTH DIAGNOSTIC ==={RESET}\n")

    # 1. Audit Checks
    api_process_active = inspect_active_processes()
    root_status, root_data = check_local_endpoint("/")
    re_status, _ = check_local_endpoint("/api/metrics")
    ac_status, _ = check_local_endpoint("/api/students")

    # Formulate localized logging statuses for text readout safely
    status_text = "RUNNING" if api_process_active else "OFFLINE"
    status_color = GREEN if api_process_active else RED
    print(f"[*] Process Status: {status_color}{status_text}{RESET}")

    port_text = "CONNECTED" if root_status == 200 else "UNREACHABLE"
    port_color = GREEN if root_status == 200 else RED
    print(f"[*] Base Port Connection: {port_color}{port_text}{RESET}")

    # Evaluate global pipeline stability
    system_healthy = api_process_active and (root_status == 200) and (re_status == 200) and (ac_status == 200)

    # 2. Compile Discord Fields Payload Matrix
    status_fields = [
        {"name": "Background API Daemon", "value": "🟢 Active running" if api_process_active else "🔴 Process Terminated", "inline": True},
        {"name": "Core Root Bound Port", "value": "🟢 Port 5005 Open" if root_status == 200 else "🔴 Port Unreachable", "inline": True},
        {"name": "Real Estate Data Endpoint", "value": "✅ Functional (200)" if re_status == 200 else "❌ Connection Error", "inline": False},
        {"name": "Academic Data Endpoint", "value": "✅ Functional (200)" if ac_status == 200 else "❌ Connection Error", "inline": False}
    ]

    # 3. Handle Alert Execution Criteria
    if system_healthy:
        print(f"\n{GREEN}{BOLD}[SUCCESS] Core system parameters are operational.{RESET}\n")
        # Optional: Uncomment the next line if you want positive sync confirmation on Discord too!
        # dispatch_discord_alert("🟢 System Status: Normal", "All infrastructure networks are operational.", 3066993, status_fields)
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}[CRITICAL] Degradation noticed! Triggering channel webhook notification...{RESET}\n")
        # 15158332 maps to an enterprise alert red color layout
        dispatch_discord_alert(
            "🚨 CRITICAL ALARM: Infrastructure Degradation Detected",
            "An internal monitoring audit has caught an offline state or port block in your background processes.",
            15158332,
            status_fields
        )
        sys.exit(1)

if __name__ == "__main__":
    run_system_diagnostic()

