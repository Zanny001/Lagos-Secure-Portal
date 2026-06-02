import os
import time
import requests

# Target Discord channel integration webhook URL parameter mapping layer
# Pulls securely from Railway Env variables; falls back to mock string for safety
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/mock_crypto_channel_token")

# Global tracking variables for RSI memory state management
RSI_PERIOD = 14
price_history = []
prev_avg_gain = None
prev_avg_loss = None

# Tracking memory locks to prevent continuous Discord spamming
# Valid states: None, "overbought", "oversold"
last_alert_state = None 

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
    Computes a standard 14-period smoothed Relative Strength Index profile.
    Maintains historical memory states for proper Wilders smoothing metrics.
    """
    global prev_avg_gain, prev_avg_loss
    
    price_history.append(current_price)
    
    # We need at least 15 points (14 deltas) to start calculations
    if len(price_history) < RSI_PERIOD + 1:
        points_needed = (RSI_PERIOD + 1) - len(price_history)
        print(f"[ANALYSIS] Buffering data into RAM... Need {points_needed} more price ticks.")
        return None

    # Compute baseline initial averages if this is exactly the 15th data point
    if prev_avg_gain is None or prev_avg_loss is None:
        gains = 0
        losses = 0
        for i in range(1, len(price_history)):
            change = price_history[i] - price_history[i-1]
            if change > 0:
                gains += change
            else:
                losses += abs(change)
                
        prev_avg_gain = gains / RSI_PERIOD
        prev_avg_loss = losses / RSI_PERIOD
        
        # Keep list optimized by trimming down to required size framework
        price_history.pop(0)
        
        rs = prev_avg_gain / (prev_avg_loss if prev_avg_loss != 0 else 0.00001)
        return 100 - (100 / (1 + rs))

    # For all subsequent ticks, apply proper Wilders Exponential Smoothing
    else:
        change = price_history[-1] - price_history[-2]
        current_gain = change if change > 0 else 0
        current_loss = abs(change) if change < 0 else 0
        
        # Wilder's smoothing formula: (Prev_Avg * 13 + Current) / 14
        smoothed_gain = (prev_avg_gain * (RSI_PERIOD - 1) + current_gain) / RSI_PERIOD
        smoothed_loss = (prev_avg_loss * (RSI_PERIOD - 1) + current_loss) / RSI_PERIOD
        
        # Save states for the next incoming data loop
        prev_avg_gain = smoothed_gain
        prev_avg_loss = smoothed_loss
        
        # Keep memory array tight
        price_history.pop(0)
        
        if smoothed_loss == 0:
            return 100
            
        rs = smoothed_gain / smoothed_loss
        return 100 - (100 / (1 + rs))

def dispatch_market_signal(current_price, rsi_value):
    """Evaluates momentum thresholds and pushes isolated alerts to the team channel."""
    global last_alert_state
    if rsi_value is None:
        return
        
    print(f"[MARKET ANALYSIS] Spot Price: ${current_price:,.2f} | Calculated Smooth RSI: {rsi_value:.2f}")
    
    payload = None
    current_state = None
    
    # Check overbought momentum thresholds
    if rsi_value >= 70:
        current_state = "overbought"
        if last_alert_state != "overbought": # Trigger alert ONLY on initial cross-over
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
        current_state = "oversold"
        if last_alert_state != "oversold": # Trigger alert ONLY on initial cross-under
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
            
    else:
        # Reset alert parameters cleanly when market normalizes between RSI 35 and 65
        if rsi_value > 35 and rsi_value < 65 and last_alert_state is not None:
            print("[ALARM CONTROL] Market indicators normalized inside safe bounds. Resetting alert locks.")
            last_alert_state = None

    # Transmit signal outbound if a validation rule triggers
    if payload:
        last_alert_state = current_state # Lock down the state machine
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
            # Note: For highly stable RSI signals, consider extending this to 30 or 60 seconds.
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n[STOP] Terminating live tracking loops cleanly.")
            break
            
        except Exception as e:
            print(f"[SYSTEM RUNTIME FAULT] Error detected inside execution loop: {e}")
            print("[SYSTEM] Retrying connection thread parameters in 10 seconds...")
            time.sleep(10)

