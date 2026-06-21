import os
import time
import requests
from datetime import datetime

# ===================================================================
# ZANNIE ALGORITHMIC FINTECH INFRASTRUCTURE
# ===================================================================

# Strict Environment Variable Execution
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
POLL_INTERVAL_SECONDS = 300  # 5 Minutes

def fetch_market_data():
    """Retrieves live metrics from public exchanges (CoinGecko API fallback)."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[-] Data fetch failed: {e}")
        return None

def dispatch_signal(data):
    """Compiles market data into an institutional-grade Discord payload."""
    if not WEBHOOK_URL:
        print("[-] DISCORD_WEBHOOK_URL is not set. Execution halted.")
        return

    btc_price = data.get("bitcoin", {}).get("usd", 0)
    btc_change = data.get("bitcoin", {}).get("usd_24h_change", 0)
    eth_price = data.get("ethereum", {}).get("usd", 0)
    eth_change = data.get("ethereum", {}).get("usd_24h_change", 0)

    # Determine trend colors
    color = 0x2ea043 if btc_change > 0 else 0xe36209

    embed = {
        "title": "⚡ Zannie Market Pulse: Institutional Feed",
        "color": color,
        "fields": [
            {
                "name": "Bitcoin (BTC)",
                "value": f"${btc_price:,.2f} ({btc_change:+.2f}%)",
                "inline": True
            },
            {
                "name": "Ethereum (ETH)",
                "value": f"${eth_price:,.2f} ({eth_change:+.2f}%)",
                "inline": True
            }
        ],
        "footer": {"text": f"Zannie Crypto Matrix • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"}
    }

    payload = {
        "username": "Zannie Execution Engine",
        "embeds": [embed]
    }

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
        print(f"[+] Signal Dispatched: BTC @ ${btc_price:,.2f}")
    except Exception as e:
        print(f"[-] Payload transmission failed: {e}")

def ignite_daemon():
    print("[*] Zannie Crypto Matrix Initialized. Polling markets...")
    while True:
        market_data = fetch_market_data()
        if market_data:
            dispatch_signal(market_data)
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    ignite_daemon()
