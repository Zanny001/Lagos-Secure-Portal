import re

file_path = "/home/userland/Lagos-Secure-Portal/realestate_api.py"

with open(file_path, "r") as f:
    content = f.read()

new_crypto_func = """@app.route('/api/v1/dashboard/crypto', methods=['GET'])
def get_crypto_telemetry():
    try:
        is_active = check_process("crypto_signal_bot.py")
        if not is_active:
            # Return offline status if the bot is killed
            return jsonify({"status": "success", "data": [
                {"asset": "SYSTEM OFFLINE", "price": 0.00, "change_24h": 0.00, "status": "OFFLINE"}
            ]}), 200

        # Fetch LIVE data from Binance
        symbols = '["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT"]'
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbols={symbols}"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            crypto_data = []
            for coin in data:
                asset_name = coin['symbol'].replace('USDT', ' / USD')
                price = float(coin['lastPrice'])
                change = float(coin['priceChangePercent'])
                status = "BULLISH" if change > 0 else "BEARISH"
                
                crypto_data.append({
                    "asset": asset_name,
                    "price": round(price, 4) if price < 1 else round(price, 2),
                    "change_24h": round(change, 2),
                    "status": status
                })
            return jsonify({"status": "success", "data": crypto_data}), 200
        else:
            raise Exception("API blocked or failed")
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

# Replace the old function with the new one
content = re.sub(r"@app\.route\('/api/v1/dashboard/crypto'.*?500", new_crypto_func, content, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(content)

print("API script updated with live Binance telemetry.")
