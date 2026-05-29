import os
import time
import json
import urllib.request

# Configuration Matrix - Replace with your actual live Discord Webhook URL string
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

# Target Tracking Thresholds (Percentage Change Limit)
VOLATILITY_THRESHOLD_PCT = 2.0  # Trigger alert if asset moves >= 2.0%

# Baseline Asset Tracking Memory Cache
price_cache = {
    "BTC": 0.0,
    "ETH": 0.0,
    "SOL": 0.0
}

# Metadata Profile Map for Presentation Display
asset_metadata = {
    "BTC": {"name": "Bitcoin", "api_id": "bitcoin"},
    "ETH": {"name": "Ethereum", "api_id": "ethereum"},
    "SOL": {"name": "Solana", "api_id": "solana"}
}

def fetch_live_market_prices():
    """
    Fetches raw, real-time crypto price feeds from CoinGecko's public exchange API 
    using lightweight built-in urllib utilities for mobile environments.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    "BTC": float(data["bitcoin"]["usd"]),
                    "ETH": float(data["ethereum"]["usd"]),
                    "SOL": float(data["solana"]["usd"])
                }
    except Exception as e:
        print(f"[API ERROR] Failed to fetch live crypto feeds: {e}")
        return None

def dispatch_discord_embed(ticker, old_price, new_price, pct_change):
    """
    Dispatches a professional, structured embed notification card 
    with clear directional flags directly to your Discord webhook channel.
    """
    direction = "🚀 SURGE BREAKOUT" if pct_change > 0 else "⚠️ DUMP BREAKOUT"
    color_code = 3066993 if pct_change > 0 else 15158332  # Green for Surge, Red for Dump

    payload = {
        "username": "Zannie Volatility Watchdog",
        "avatar_url": "https://i.imgur.com/w8p6m9B.png",
        "embeds": [
            {
                "title": f"🔔 Market Alert: {ticker}/USD ({asset_metadata[ticker]['name']})",
                "description": f"Real-time volatility monitoring has registered a breakout violating your configured boundary.",
                "color": color_code,
                "fields": [
                    {"name": "Action Matrix", "value": f"**{direction}**", "inline": True},
                    {"name": "Percentage Shift", "value": f"`{pct_change:+.2f}%`", "inline": True},
                    {"name": "Previous Price Base", "value": f"${old_price:,.2f}", "inline": True},
                    {"name": "Trigger Price Break", "value": f"${new_price:,.2f}", "inline": True}
                ],
                "footer": {
                    "text": f"Zannie Crypto Engine Node • {time.strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
        ]
    }

    # Format payload structural block
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL, 
        data=data, 
        headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 204]:
                print(f"[+ Webhook] Discord embed alert successfully forwarded for {ticker}.")
    except Exception as e:
        print(f"[-] Webhook communication breakdown: {e}")

def monitor_market_loop():
    print(f"[*] Initializing Zannie Crypto Volatility Monitor Node (Barrier: {VOLATILITY_THRESHOLD_PCT}%)...")

    # Run initial seed scan to populate memory array pointers
    initial_prices = fetch_live_market_prices()
    if initial_prices:
        for ticker in price_cache:
            price_cache[ticker] = initial_prices[ticker]
        print(f"[+] Initial market baseline cache mapped: {price_cache}")
    else:
        print("[-] Warning: Failed to fetch initial price baseline markers.")

    while True:
        time.sleep(60)  # Scan the market live every 60 seconds
        live_prices = fetch_live_market_prices()
        if not live_prices:
            continue

        for ticker in price_cache:
            last_price = price_cache[ticker]
            current_price = live_prices[ticker]

            if last_price == 0.0:
                price_cache[ticker] = current_price
                continue

            # Calculate precise mathematical percentage variation
            percent_change = ((current_price - last_price) / last_price) * 100

            print(f"[🔍 Scanning] {ticker}: Last=${last_price:,.2f} -> Current=${current_price:,.2f} ({percent_change:+.2f}%)")

            # Check if variation steps past the barrier threshold configuration
            if abs(percent_change) >= VOLATILITY_THRESHOLD_PCT:
                print(f"[!] Breakout breach detected on {ticker}!")
                dispatch_discord_embed(ticker, last_price, current_price, percent_change)
                
                # Update memory cache pointer to prevent redundant alerts
                price_cache[ticker] = current_price

if __name__ == "__main__":
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("[WARNING] Update your DISCORD_WEBHOOK_URL variable endpoint before executing engine tracking loops.")
    monitor_market_loop()

