import os
import hmac
import hashlib
import uuid
import sqlite3
from flask import Flask, request, jsonify
# Import your database tools and initialization function
from zannie_db import create_pending_order, log_successful_payment, init_zannie_database
# Import your automated notification engine
from zannie_notifier import dispatch_order_notifications

app = Flask('zannie_brand')

# Ensure tables exist inside zannie_sales.db when the Flask app spins up
init_zannie_database()

# Retrieve secret key from environment variables (fallback to test placeholder)
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_mock_secret_key_zannie")

@app.route('/api/v1/checkout/initialize', methods=['POST'])
def initialize_checkout():
    """
    Route 1: Endpoint to start a checkout session.
    Generates a unique tracking reference, saves it as PENDING in zannie_sales.db,
    and returns authorization payload details back to the client.
    """
    data = request.get_json()
    if not data or 'email' not in data or 'amount' not in data:
        return jsonify({"status": "error", "message": "Malformed payload structure"}), 400
        
    email = data['email']
    amount_kobo = data['amount']
    currency = data.get('currency', 'NGN')
    
    # Generate a clean, unique tracking reference string for your Zannie storefront
    order_id = f"ZAN-{uuid.uuid4().hex[:8].upper()}"
    
    # 1. Commit the pending transaction track record to your database file
    db_success = create_pending_order(order_id, email, amount_kobo, currency)
    
    if not db_success:
        return jsonify({"status": "error", "message": "Database allocation failure"}), 500

    print(f"[GATEWAY] Pending order initialized: {order_id} for {email}")
    return jsonify({
        "status": "success",
        "message": "Checkout tracking active",
        "data": {
            "order_id": order_id,
            "authorization_url": f"https://checkout.paystack.com/mock-gateway-{order_id}",
            "reference": order_id
        }
    }), 200

@app.route('/api/v1/payments/webhook', methods=['POST'])
def paystack_webhook():
    """
    Route 2: Live secure Webhook listener endpoint.
    Verifies signatures cryptographically and fires automated notification events.
    """
    payload = request.get_data()
    paystack_signature = request.headers.get('X-Paystack-Signature')

    if not paystack_signature:
        print("[SECURITY ALERT] Received unsigned webhook payload metadata.")
        return jsonify({"status": "error", "message": "Missing verification signature"}), 401

    # Constant-time HMAC SHA512 signature verification block to prevent timing attacks
    computed_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, paystack_signature):
        print("[SECURITY ALERT] Signature mismatch detected on incoming webhook data packet.")
        return jsonify({"status": "error", "message": "Invalid transaction token signature"}), 401

    # Extract event payload safely after verification checks clear
    event_data = request.get_json()
    
    if event_data and event_data.get('event') == 'charge.success':
        data_block = event_data.get('data', {})
        reference = data_block.get('reference')  # This holds the order_id sent during checkout
        amount_kobo = data_block.get('amount')
        gateway_msg = data_block.get('gateway_response', 'Approved')

        print(f"[WEBHOOK SIGNED] Confirmed success event. Processing transaction ref: {reference}")
        
        # 2. Update status to PAID in the database ledger
        db_updated = log_successful_payment(reference, reference, amount_kobo, gateway_msg)
        
        # 3. Handle fulfillment notification tasks transparently
        try:
            conn = sqlite3.connect("zannie_sales.db")
            cursor = conn.cursor()
            cursor.execute("SELECT customer_email, status FROM orders WHERE order_id = ?", (reference,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                customer_email = row[0]
                current_status = row[1]
                
                if db_updated:
                    print(f"[GATEWAY] First-time payment tracking processing for order {reference}.")
                    dispatch_order_notifications(reference, customer_email, amount_kobo)
                elif current_status == 'PAID':
                    print(f"[GATEWAY ALERT] Webhook duplicate received for order {reference}. Re-running notifications trail.")
                    dispatch_order_notifications(reference, customer_email, amount_kobo)
            else:
                print(f"[GATEWAY WARN] Webhook reference {reference} not found in historical orders table.")
                
        except sqlite3.Error as e:
            print(f"[GATEWAY ERROR] Failed to query customer context for notification dispatch: {e}")

    return jsonify({"status": "success", "message": "Webhook acknowledged cleanly"}), 200

if __name__ == "__main__":
    # Runs locally on port 5001 linked directly with your ngrok endpoint
    app.run(host='0.0.0.0', port=5001, debug=True)

