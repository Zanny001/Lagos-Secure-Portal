import requests
import time
import datetime

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1508242341117300817/OjaNgS8SBM9TUuoOE0jDgprS-MObnqiSvYzrgAy9EGiJ1Rl2SusVDjvEISHjDYNH6Hb6"
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/24hr"
TARGET_ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
VOLATILITY_THRESHOLD = 2.0  # Alert if 24h change is > 2%
PRICE_MOVE_THRESHOLD = 1.0  # Subsequent alerts trigger only if price moves another 1% up/down

# InMemory State Tracker to prevent 5-minute spamming
last_alerted_prices = {asset: 0.0 for asset in TARGET_ASSETS}

def fetch_market_data():
    try:
        response = requests.get(BINANCE_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Binance API Error: {e}")
        return []

def send_signal(asset, price, change, direction):
    color = 5763719 if direction == "UP" else 15548997 # Green or Red
    emoji = "📈" if direction == "UP" else "📉"

    payload = {
        "username": "Zannie Central Console",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/6001/6001368.png",
        "content": f"🚨 **Zany's Crypto Market Signal** 🚨",
        "embeds": [{
            "title": f"{emoji} Volatility Alert: {asset}",
            "description": f"Significant market movement detected on the Binance network.",
            "color": color,
            "fields": [
                {"name": "Current Value", "value": f"${price:,.2f}", "inline": True},
                {"name": "24H Delta", "value": f"{change}%", "inline": True}
            ],
            "footer": {"text": f"Zannie Digital Automation System • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        }]
    }

    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code in [200, 204]:
            print(f"[{datetime.datetime.now()}] Signal transmitted to Discord for {asset}.")
        else:
            print(f"[{datetime.datetime.now()}] Discord Webhook returned status code: {res.status_code}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Webhook failure: {e}")

def monitor_loop():
    print("Zannie Smart Discord Notifier initialized. Monitoring market swings safely...")
    while True:
        data = fetch_market_data()
        for item in data:
            symbol = item['symbol']
            if symbol in TARGET_ASSETS:
                change_pct = float(item['priceChangePercent'])
                current_price = float(item['lastPrice'])
                asset_name = symbol.replace("USDT", "")

                # Base check: Is 24h movement significant?
                if abs(change_pct) >= VOLATILITY_THRESHOLD:
                    last_price = last_alerted_prices[symbol]
                    
                    # If we haven't alerted yet, or if price moved significantly from our last alert
                    should_alert = False
                    direction = "UP" if change_pct > 0 else "DOWN"
                    
                    if last_price == 0.0:
                        should_alert = True
                    else:
                        # Compute percentage change from the last alert price
                        price_delta = abs((current_price - last_price) / last_price) * 100
                        if price_delta >= PRICE_MOVE_THRESHOLD:
                            should_alert = True
                            # Readjust direction based on direct price action velocity
                            direction = "UP" if current_price > last_price else "DOWN"

                    if should_alert:
                        last_alerted_prices[symbol] = current_price
                        send_signal(asset_name, current_price, change_pct, direction)

        # Poll every 60 seconds for tighter volatility tracking without channel spam
        time.sleep(60)

if __name__ == "__main__":
    if "YOUR_DISCORD_WEBHOOK_URL" in DISCORD_WEBHOOK_URL:
        print("SYSTEM HALT: Please insert your valid Discord Webhook URL into the script.")
    else:
        monitor_loop()
