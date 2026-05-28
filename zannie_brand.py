import os, json, hmac, hashlib, requests
from flask import Flask, request, jsonify
from rate_limiter import SlidingWindowLimiter, limit_requests

app = Flask(__name__)

# Instantiate a rate limiter tracking window: Max 3 checkout attempts per 15 seconds
checkout_limiter = SlidingWindowLimiter(window_seconds=15, max_requests=3)

PAYSTACK_SECRET_KEY = "sk_live_sample_zannie_key_99182"
PAYSTACK_WEBHOOK_SECRET = "whsec_zannie_signature_verification_token"

@app.route("/api/v1/checkout/initialize", methods=["POST"])
@limit_requests(checkout_limiter)
def initialize_checkout():
    data = request.get_json() or {}
    base_price_usd = 85.00  
    selected_currency = data.get("currency", "NGN").upper()
    
    payable_amount = int(base_price_usd * 1500 * 100) if selected_currency == "NGN" else int(base_price_usd * 100)

    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
    payload = {"email": data.get("email"), "amount": payable_amount, "currency": selected_currency}

    try:
        response = requests.post(paystack_url, json=payload, headers=headers, timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Upstream channel connection error: {e}"}), 502

@app.route("/api/v1/payments/webhook", methods=["POST"])
def paystack_webhook_listener():
    payload_signature = request.headers.get("x-paystack-signature")
    if not payload_signature: return jsonify({"status": "unauthorized"}), 401
        
    computed_signature = hmac.new(
        key=PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
        msg=request.data,
        digestmod=hashlib.sha512
    ).hexdigest()
    
    if not hmac.compare_digest(computed_signature, payload_signature):
        return jsonify({"status": "forbidden"}), 403

    event_data = json.loads(request.data)
    if event_data.get("event") == "charge.success":
        print(f"[💰 PAYMENT VERIFIED] Dispatching Order Fulfillment Pipeline.")
        
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
