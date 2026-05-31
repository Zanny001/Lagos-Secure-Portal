import os
import sqlite3
import json
import requests
from flask import Flask, jsonify, send_from_directory, request

app = Flask(__name__)

# ==============================================================================
# MASTER CONFIGURATIONS & COMPONENT PATHS
# ==============================================================================
REALESTATE_DB = "realestate_analytics.db"
ACADEMIC_DB = "academic_analytics.db"
PORTAL_ROOT = "/home/userland/Lagos-Secure-Portal"
EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/NGN"

DEFAULT_CURRENCY_CACHE = {
    "NGN": 1.0,
    "USD": 0.00067,
    "GBP": 0.00053,
    "EUR": 0.00062
}

def query_database(db_path, query, args=()):
    """Safely handles connections and extracts rows from target SQLite database nodes."""
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[-] Database query failure on {db_path}: {e}")
        return []

def fetch_live_exchange_rates():
    """Fetches real-time currency conversion matrices using NGN as the base denomination."""
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=4)
        if response.status_code == 200:
            rates = response.json().get("rates", {})
            return {cur: rates[cur] for cur in DEFAULT_CURRENCY_CACHE if cur in rates}
    except Exception as e:
        print(f"[-] Exchange rate sync timed out: {e}. Utilizing fallback parameters.")
    return DEFAULT_CURRENCY_CACHE

# ==============================================================================
# GLOBAL CORS MIDDLEWARE INFRASTRUCTURE
# ==============================================================================
@app.after_request
def apply_global_cors_headers(response):
    """Injects CORS compliance headers to allow seamless cross-origin traffic via public tunnels."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Bypass-Tunnel-Reminder"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# ==============================================================================
# REAL ESTATE & ACADEMIC TRACKING ENDPOINTS
# ==============================================================================
@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Public cross-origin network endpoint serving structured market trends."""
    query = """
        SELECT location, average_price as price, active_listings as listings,
               classification as class, service_charge, total_area_sqm, price_per_sqm
        FROM location_metrics
    """
    data = query_database(REALESTATE_DB, query)
    if not data:
        return jsonify([
            {"location": "Lekki Phase 1 Sector", "price": 125000000.0, "listings": 14, "class": "Premium Residential", "service_charge": 2500000.0, "total_area_sqm": 400.0, "price_per_sqm": 312500.0},
            {"location": "Alaba International Segment", "price": 45000000.0, "listings": 28, "class": "Commercial Hub", "service_charge": 0.0, "total_area_sqm": 120.0, "price_per_sqm": 375000.0}
        ])
    return jsonify(data)

@app.route('/api/students', methods=['GET'])
def get_student_metrics():
    """Public endpoint serving unified academic telemetry metrics."""
    query = "SELECT student_name, syllabus_type, average_score, attendance_rate FROM student_metrics"
    rows = query_database(ACADEMIC_DB, query)
    if rows is None:
        return jsonify({"error": "Academic tracker database node unseeded or unreachable"}), 404
    payload = [{"name": r["student_name"], "track": r["syllabus_type"], "average": r["average_score"], "attendance": r["attendance_rate"]} for r in rows]
    return jsonify(payload)

@app.route('/api/syllabus', methods=['GET'])
def get_syllabus_manifest():
    try:
        with open(os.path.join(PORTAL_ROOT, 'lessons_manifest.json'), 'r', encoding='utf-8') as f:
            return jsonify(json.load(f)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==============================================================================
# INTERNATIONAL E-COMMERCE GATEWAY LAYER (ZANNIE BRAND)
# ==============================================================================
@app.route('/api/zannie/product-price', methods=['POST'])
def calculate_localized_price():
    """Accepts a base price in NGN and outputs dynamic global currency conversions."""
    data = request.get_json() or {}
    base_price_ngn = data.get("base_price_ngn")
    target_currency = data.get("target_currency", "NGN").upper()

    if base_price_ngn is None:
        return jsonify({"status": "error", "message": "Missing key: base_price_ngn"}), 400

    rates = fetch_live_exchange_rates()
    if target_currency not in rates:
        return jsonify({"status": "error", "message": f"Unsupported currency configuration. Options: {list(rates.keys())}"}), 400

    conversion_factor = rates[target_currency]
    converted_amount = round(float(base_price_ngn) * conversion_factor, 2)
    return jsonify({
        "status": "success", "base_currency": "NGN", "base_price": float(base_price_ngn),
        "target_currency": target_currency, "exchange_rate": conversion_factor, "converted_amount": converted_amount
    }), 200

@app.route('/api/zannie/checkout', methods=['POST'])
def initialize_international_checkout():
    """Validates global customer entries and maps payloads for Paystack/Flutterwave APIs."""
    data = request.get_json() or {}
    customer_email = data.get("email")
    total_amount_ngn = data.get("amount_ngn")
    selected_currency = data.get("currency", "NGN").upper()

    if not customer_email or not total_amount_ngn:
        return jsonify({"status": "error", "message": "Compulsory arguments missing: email and amount_ngn"}), 400

    rates = fetch_live_exchange_rates()
    conversion_rate = rates.get(selected_currency, 1.0)
    final_settlement_value = round(float(total_amount_ngn) * conversion_rate, 2)

    gateway_payload = {
        "email": customer_email,
        "amount": int(final_settlement_value * 100),  # Gateways compute in minor denominations (kobo/cents)
        "currency": selected_currency,
        "metadata": {
            "custom_fields": [
                {"display_name": "Brand Origin", "variable_name": "brand", "value": "Zannie Fashion International"},
                {"display_name": "Base Valuation", "variable_name": "base_ngn", "value": f"NGN {total_amount_ngn}"}
            ]
        }
    }
    return jsonify({
        "status": "success", "message": "Cross-border payment pipeline established.",
        "gateway_payload": gateway_payload,
        "payment_url_mock": f"https://checkout.gatewayserver.com/pay/zannie_secure_{int(final_settlement_value)}"
    }), 200

# ==============================================================================
# DYNAMIC FRONTEND UI STATIC FILE ROUTING LAYER
# ==============================================================================
@app.route('/', methods=['GET'])
def serve_default_hub():
    if os.path.exists(os.path.join(PORTAL_ROOT, "index.html")):
        return send_from_directory(PORTAL_ROOT, "index.html")
    return jsonify({"status": "online", "node_owner": "Elebute Hassan Oluwafemi", "active_modules": ["Analytics Hub", "Zannie Commerce Platform"]})

@app.route('/<path:filename>', methods=['GET'])
def serve_portal_html_pages(filename):
    if os.path.exists(os.path.join(PORTAL_ROOT, filename)):
        return send_from_directory(PORTAL_ROOT, filename)
    return jsonify({"error": f"Asset target path '{filename}' is unreachable on this server infrastructure partition."}), 404

if __name__ == '__main__':
    print("[*] Launching Unified Core API and Web Engine on Port 5005...")
    app.run(host='0.0.0.0', port=5005, debug=False)
