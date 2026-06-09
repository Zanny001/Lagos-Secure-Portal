import os
import sqlite3
import json
import requests
import subprocess
import random
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PORTAL_ROOT = "/home/userland/Lagos-Secure-Portal"
REALESTATE_DB = os.path.join(PORTAL_ROOT, "realestate_analytics.db")
ACADEMIC_DB = os.path.join(PORTAL_ROOT, "academic_analytics.db")
DEALS_DB = os.path.join(PORTAL_ROOT, "deal_harvester.db")
EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/NGN"

DEFAULT_CURRENCY_CACHE = {
    "NGN": 1.0, "USD": 0.00067, "GBP": 0.00053, "EUR": 0.00062
}

def check_process(pattern):
    try:
        res = subprocess.run(["pgrep", "-f", pattern], stdout=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def fetch_live_exchange_rates():
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=4)
        if response.status_code == 200:
            rates = response.json().get("rates", {})
            return {cur: rates[cur] for cur in DEFAULT_CURRENCY_CACHE if cur in rates}
    except Exception:
        pass
    return DEFAULT_CURRENCY_CACHE

@app.after_request
def apply_global_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Bypass-Tunnel-Reminder"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# ==============================================================================
# DEVOPS SYSTEM HUB ENGINE
# ==============================================================================
@app.route('/api/v1/dashboard/status', methods=['GET'])
def get_dashboard_status():
    return jsonify({
        "crawler": check_process("realestate_crawler.py"),
        "crypto": check_process("crypto_signal_bot.py"),
        "harvester": check_process("live_monitor.py"),
        "api": True,
        "http": check_process("http.server 8080"),
        "verify": check_process("node server.js")
    }), 200

@app.route('/api/v1/dashboard/execute', methods=['POST'])
def execute_dashboard_action():
    data = request.get_json() or {}
    action = str(data.get('action', ''))
    msg = "Action sequence unrecognized"

    if action == "1":
        if not check_process("realestate_crawler.py"):
            subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/scrapers/realestate_crawler.py"], stdout=subprocess.DEVNULL)
            msg = "Real Estate Crawler daemon successfully triggered."
        else: msg = "Crawler pipeline already operational."
    elif action == "5":
        subprocess.run(["pkill", "-f", "realestate_crawler.py"])
        msg = "Real Estate Crawler processes terminated safely."
    elif action == "2":
        if not check_process("crypto_signal_bot.py"):
            subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/bots/crypto_signal_bot.py"], stdout=subprocess.DEVNULL)
            msg = "Crypto volatility tracking engines initialized."
        else: msg = "Crypto bot streaming matrix already running."
    elif action == "6":
        subprocess.run(["pkill", "-f", "crypto_signal_bot.py"])
        msg = "Crypto volatility tracking systems deactivated."
    elif action == "3": msg = "Core System Hub API is already running online on Port 5005."
    elif action == "4":
        if not check_process("http.server 8080"):
            subprocess.Popen(["python3", "-m", "http.server", "8080"], cwd=PORTAL_ROOT, stdout=subprocess.DEVNULL)
            msg = "Local Sandboxed Server bound to Port 8080."
        else: msg = "HTTP Sandbox on Port 8080 already listening."
    elif action == "8":
        subprocess.run(["pkill", "-f", "http.server 8080"])
        msg = "HTTP Port 8080 Web Server terminated."
    elif action == "9":
        if not check_process("node server.js"):
            subprocess.Popen(["node", "server.js"], cwd=PORTAL_ROOT, stdout=subprocess.DEVNULL)
            msg = "Lagos Secure Verify Node booted on Port 5000."
        else: msg = "Secure Verify Node already running on Port 5000."
    elif action == "10":
        subprocess.run(["pkill", "-f", "node server.js"])
        msg = "Lagos Secure Verify Node stopped."
    elif action == "12":
        subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/maintenance/compile_academic_stats.py"], stdout=subprocess.DEVNULL)
        msg = "Markdown report rebuild loop initialized."
    elif action == "13":
        subprocess.Popen(["bash", f"{PORTAL_ROOT}/scripts/bash/system_maintenance.sh"], stdout=subprocess.DEVNULL)
        msg = "Database rotations and background log back-ups triggered."
    elif action == "14":
        if not check_process("live_monitor.py"):
            subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/bots/live_monitor.py"], stdout=subprocess.DEVNULL)
            msg = "Deal Harvester Pipeline actively hunting margins."
        else: msg = "Deal Harvester is already running."
    elif action == "15":
        subprocess.run(["pkill", "-f", "live_monitor.py"])
        msg = "Deal Harvester Pipeline terminated safely."
    elif action == "A":
        if not check_process("realestate_crawler.py"): subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/scrapers/realestate_crawler.py"], stdout=subprocess.DEVNULL)
        if not check_process("crypto_signal_bot.py"): subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/bots/crypto_signal_bot.py"], stdout=subprocess.DEVNULL)
        if not check_process("live_monitor.py"): subprocess.Popen(["python3", f"{PORTAL_ROOT}/scripts/bots/live_monitor.py"], stdout=subprocess.DEVNULL)
        if not check_process("http.server 8080"): subprocess.Popen(["python3", "-m", "http.server", "8080"], cwd=PORTAL_ROOT, stdout=subprocess.DEVNULL)
        if not check_process("node server.js"): subprocess.Popen(["node", "server.js"], cwd=PORTAL_ROOT, stdout=subprocess.DEVNULL)
        msg = "Global boot macro deployment run finished successfully. All paths launched."
    elif action == "K":
        subprocess.run(["pkill", "-f", "realestate_crawler.py"])
        subprocess.run(["pkill", "-f", "crypto_signal_bot.py"])
        subprocess.run(["pkill", "-f", "live_monitor.py"])
        subprocess.run(["pkill", "-f", "http.server 8080"])
        subprocess.run(["pkill", "-f", "node server.js"])
        msg = "All detached daemon tasks downscaled and killed."

    return jsonify({"status": "executed", "message": msg}), 200

# ==============================================================================
# DATA PIPELINES 
# ==============================================================================
@app.route('/api/v1/dashboard/metrics', methods=['GET'])
def get_market_metrics():
    try:
        conn = sqlite3.connect(REALESTATE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT location, average_price, active_listings, classification, last_updated FROM location_metrics")
        rows = cursor.fetchall()
        conn.close()
        metrics = [{"location": r[0], "average_price": r[1], "active_listings": r[2], "classification": r[3]} for r in rows]
        return jsonify({"status": "success", "data": metrics}), 200
    except:
        return jsonify({"status": "error"}), 500

@app.route('/api/v1/dashboard/crypto', methods=['GET'])
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
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v1/dashboard/deals', methods=['GET'])
def get_harvested_deals():
    try:
        import sqlite3
        db_path = "/home/userland/Lagos-Secure-Portal/deal_harvester.db"
        
        if not os.path.exists(db_path):
            return jsonify({"status": "success", "data": []}), 200
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT device_name, original_price, discount_price, savings_percent, affiliate_link FROM active_deals")
        rows = c.fetchall()
        conn.close()
        
        deals_list = []
        for row in rows:
            deals_list.append({
                "device": row[0],
                "original": row[1],
                "discount": row[2],
                "savings": row[3],
                "link": row[4]
            })
            
        return jsonify({"status": "success", "data": deals_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v1/store/rates', methods=['GET'])
def get_store_exchange_rates():
    return jsonify({"status": "success", "base": "NGN", "rates": fetch_live_exchange_rates()}), 200

@app.route('/', methods=['GET'])
def serve_default_hub():
    if os.path.exists(os.path.join(PORTAL_ROOT, "dashboard_index.html")):
        return send_from_directory(PORTAL_ROOT, "dashboard_index.html")
    return jsonify({"status": "online"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
