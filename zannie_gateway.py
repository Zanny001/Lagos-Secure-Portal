import os
import json
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Sandbox API keys placeholder for payment gateway handlers
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "sk_test_zannie_international_secure_token")
EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/NGN"

# In-memory fallback currency cache if third-party exchange rate APIs time out
DEFAULT_CURRENCY_CACHE = {
    "NGN": 1.0,
    "USD": 0.00067,  # Sample dynamic conversion base indices
    "GBP": 0.00053,
    "EUR": 0.00062
}

def fetch_live_exchange_rates():
    """Fetches real-time currency conversion matrices using NGN as base denomination."""
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=5)
        if response.status_code == 200:
            rates = response.json().get("rates", {})
            # Filter and return only our required international standard currencies
            return {cur: rates[cur] for cur in DEFAULT_CURRENCY_CACHE if cur in rates}
    except Exception as e:
        print(f"[-] Exchange rate fetch failure: {e}. Utilizing fallback cache configuration.")
    return DEFAULT_CURRENCY_CACHE

# ==============================================================================
# INTERNATIONAL TRANS-CURRENCY PRICING ROUTE
# ==============================================================================
@app.route('/api/zannie/product-price', methods=['POST'])
def calculate_localized_price():
    """
    Accepts a base price in NGN and a target customer currency token.
    Returns dynamically converted transaction value parameters.
    """
    data = request.get_json() or {}
    base_price_ngn = data.get("base_price_ngn")
    target_currency = data.get("target_currency", "NGN").upper()

    if base_price_ngn is None:
        return jsonify({"status": "error", "message": "Missing required 'base_price_ngn' property."}), 400

    rates = fetch_live_exchange_rates()
    
    if target_currency not in rates:
        return jsonify({
            "status": "error", 
            "message": f"Unsupported currency format '{target_currency}'. Supported: {list(rates.keys())}"
        }), 400

    # Calculate converted product cost
    conversion_factor = rates[target_currency]
    converted_amount = round(float(base_price_ngn) * conversion_factor, 2)

    return jsonify({
        "status": "success",
        "base_currency": "NGN",
        "base_price": float(base_price_ngn),
        "target_currency": target_currency,
        "exchange_rate": conversion_factor,
        "converted_amount": converted_amount
    }), 200

# ==============================================================================
# SECURE CROSS-BORDER CHECKOUT INTEGRATION LAYER
# ==============================================================================
@app.route('/api/zannie/checkout', methods=['POST'])
def initialize_international_checkout():
    """
    Simulates initialization of cross-border multi-currency transactions,
    mapping localized token verification rules prior to gateway handshakes.
    """
    data = request.get_json() or {}
    customer_email = data.get("email")
    total_amount_ngn = data.get("amount_ngn")
    selected_currency = data.get("currency", "NGN").upper()

    if not customer_email or not total_amount_ngn:
        return jsonify({"status": "error", "message": "Missing validation requirements: email and amount_ngn are compulsory."}), 400

    rates = fetch_live_exchange_rates()
    conversion_rate = rates.get(selected_currency, 1.0)
    final_settlement_value = round(float(total_amount_ngn) * conversion_rate, 2)

    # Simulating Paystack/Flutterwave multi-currency API request parameters
    gateway_payload = {
        "email": customer_email,
        "amount": int(final_settlement_value * 100), # Gateways typically read minor units (kobo/cents)
        "currency": selected_currency,
        "metadata": {
            "custom_fields": [
                {"display_name": "Brand", "variable_name": "brand", "value": "Zannie Fashion International"},
                {"display_name": "Base NGN Value", "variable_name": "base_ngn", "value": f"NGN {total_amount_ngn}"}
            ]
        }
    }

    print(f"[+] Initializing international checkout pipeline for {customer_email} targeting {selected_currency} context.")
    
    return jsonify({
        "status": "success",
        "message": "Transaction pipeline initialized successfully.",
        "gateway_payload": gateway_payload,
        "payment_url_mock": f"https://checkout.gatewayserver.com/pay/zannie_secure_session_{int(final_settlement_value)}"
    }), 200

if __name__ == '__main__':
    print("[*] Launching Zannie E-Commerce Payment Gateway Engine on Port 5006...")
    app.run(host='0.0.0.0', port=5006, debug=False)
