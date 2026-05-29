import time
import requests

# Your designated Discord Webhook integration channel URL
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

# Tracking cache to store the last alerted prices
price_cache = {
    "BTC": 0.0,
    "ETH": 0.0,
    "SOL": 0.0
}

# The percentage volatility trigger (e.g., 2.0%)
VOLATILITY_THRESHOLD = 2.0

def fetch_live_prices():
    """
    Fetches real-time price feeds from a public, reliable market ticker API.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return {
            "BTC": float(data["bitcoin"]["usd"]),
            "ETH": float(data["ethereum"]["usd"]),
            "SOL": float(data["solana"]["usd"])
        }
    except Exception as e:
        print(f"[API ERROR] Failed to fetch live crypto feeds: {e}")
        return None

def send_discord_alert(coin, current_price, pct_change):
    """
    Dispatches a structured signal notification card to your Discord channel.
    """
    direction = "🚀 SURGE" if pct_change > 0 else "⚠️ DUMP"
    payload = {
        "content": f"**[Zannie Crypto Intelligence Signal]**\n"
                   f"**Asset:** {coin}/USD\n"
                   f"**Action:** Market Volatility Alert ({direction})\n"
                   f"**Current Price:** ${current_price:,.2f}\n"
                   f"**Movement:** {pct_change:+.2f}% change since last major signal."
    }
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code == 240 or res.status_code == 204:
            print(f"[WEBHOOK SUCCESS] Dispatched {coin} volatility alert.")
    except Exception as e:
        print(f"[WEBHOOK ERROR] Failed to push message to Discord: {e}")

def monitor_market_loop():
    print("Initializing Zannie Crypto Volatility Monitor...")
    
    # Run an initial seed fetch to populate the baseline cache prices
    initial_prices = fetch_live_prices()
    if initial_prices:
        for coin in price_cache:
            price_cache[coin] = initial_prices[coin]
        print(f"Baseline prices cached: {price_cache}")

    while True:
        time.sleep(60) # Scan the market intervals every 60 seconds
        live_prices = fetch_live_prices()
        if not live_prices:
            continue
            
        for coin in price_cache:
            last_price = price_cache[coin]
            current_price = live_prices[coin]
            
            if last_price == 0.0:
                price_cache[coin] = current_price
                continue
                
            # Calculate the percentage change between iterations
            percent_change = ((current_price - last_price) / last_price) * 100
            
            # Trigger alert only if price movement crosses our threshold bounds
            if abs(percent_change) >= VOLATILITY_THRESHOLD:
                send_discord_alert(coin, current_price, percent_change)
                # Update the baseline cache to prevent spamming the channel
                price_cache[coin] = current_price

if __name__ == "__main__":
    # To run this in production, replace YOUR_DISCORD_WEBHOOK_URL_HERE with your link
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("[WARNING] Update your DISCORD_WEBHOOK_URL variable before executing.")
    monitor_market_loop()

