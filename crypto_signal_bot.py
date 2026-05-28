import time
import collections
import requests

# Fixed-size queue allocated completely in RAM (tracks the latest 15 price points)
price_history = collections.deque(maxlen=15)

# Target Discord channel integration webhook URL parameter mapping layer
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/mock_crypto_channel_token"

def fetch_live_bitcoin_price():
    """Queries public exchange APIs to fetch current crypto market rates."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return float(response.json()["bitcoin"]["usd"])
    except Exception as e:
        print(f"[API ERROR] Price data feed failure: {e}")
    return None

def calculate_rsi(current_price):
    """
    Computes a standard 14-period Relative Strength Index profile.
    Operates strictly in memory using floating window values.
    """
    price_history.append(current_price)
    
    # We need a minimum of 15 data points to establish a stable 14-period delta history
    if len(price_history) < 15:
        points_needed = 15 - len(price_history)
        print(f"[ANALYSIS] Buffering data into RAM... Need {points_needed} more price ticks.")
        return None
        
    gains = []
    losses = []
    
    # Calculate price movements between consecutive frames
    for i in range(1, len(price_history)):
        change = price_history[i] - price_history[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
            
    # Compute basic averages for the tracking timeframe
    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14
    
    if avg_loss == 0:
        return 100  # Prevents division by zero errors if prices only go up
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def dispatch_market_signal(current_price, rsi_value):
    """Evaluates momentum thresholds and pushes alerts to the team channel."""
    if rsi_value is None:
        return
        
    print(f"[MARKET ANALYSIS] Spot Price: ${current_price:,.2f} | Calculated RSI: {rsi_value:.2f}")
    
    payload = None
    
    # Check overbought momentum thresholds
    if rsi_value >= 70:
        payload = {
            "embeds": [{
                "title": "📈 ZANY CRITICAL BOT ALERT: OVERBOUGHT",
                "color": 16758784,  # Amber status outline indicator code
                "fields": [
                    {"name": "Asset Pair", "value": "`BTC/USD`", "inline": True},
                    {"name": "Spot Price", "value": f"${current_price:,.2f}", "inline": True},
                    {"name": "Calculated RSI (14)", "value": f"`{rsi_value:.2f}`", "inline": True}
                ],
                "footer": {"text": "Strategy: Potential Short/Reversal Signal"}
            }]
        }
    # Check oversold momentum thresholds
    elif rsi_value <= 30:
        payload = {
            "embeds": [{
                "title": "📉 ZANY CRITICAL BOT ALERT: OVERSOLD",
                "color": 3447003,  # Deep blue structural highlight code
                "fields": [
                    {"name": "Asset Pair", "value": "`BTC/USD`", "inline": True},
                    {"name": "Spot Price", "value": f"${current_price:,.2f}", "inline": True},
                    {"name": "Calculated RSI (14)", "value": f"`{rsi_value:.2f}`", "inline": True}
                ],
                "footer": {"text": "Strategy: Potential Long/Accumulation Signal"}
            }]
        }

    # Transmit signal outbound if a validation rule triggers
    if payload:
        print(f"[ALARM] Momentum threshold broken! Shipping dispatch payload card...")
        if "mock_crypto_channel_token" not in DISCORD_WEBHOOK_URL:
            try:
                response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
                if response.status_code in [200, 204]:
                    print("[ALARM] Webhook transaction completed successfully.")
            except Exception as e:
                print(f"[ALARM ERROR] Failed to send webhook alert: {e}")
        else:
            print("[ALARM] (Simulation Mode) Webhook target validated successfully.")

if __name__ == "__main__":
    print("[START] Initializing In-Memory RSI Live Analysis Engine...")
    
    # Outer core loops indefinitely to maintain runtime state persistence
    while True:
        try:
            btc_price = fetch_live_bitcoin_price()
            if btc_price:
                rsi = calculate_rsi(btc_price)
                dispatch_market_signal(btc_price, rsi)
                
            # Intercept pacing pause to stay inside public rate limits smoothly
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n[STOP] Terminating live tracking loops cleanly.")
            break
            
        except Exception as e:
            print(f"[SYSTEM RUNTIME FAULT] Error detected inside execution loop: {e}")
            print("[SYSTEM] Retrying connection thread parameters in 10 seconds...")
            time.sleep(10)

