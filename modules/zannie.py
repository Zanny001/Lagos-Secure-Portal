import uuid
import sqlite3
import requests
from flask import Blueprint, request, jsonify
from config import ZANNIE_DB, DISCORD_WEBHOOK_URL

# ===================================================================
# MODULE B: ZANNIE PREMIUM APPAREL BLUEPRINT
# ===================================================================
zannie_bp = Blueprint('zannie', __name__)

def dispatch_payment_webhook_alert(order_id, customer, item, currency, amount, gateway, reference):
    formatted_amount = f"{currency} {amount:,.2f}" if isinstance(amount, (int, float)) else f"{currency} {amount}"

    payload = {
        "embeds": [{
            "title": "💰 PREMIUM ORDER TRANSACTION CLEARED",
            "color": 3066993,
            "fields": [
                {"name": "Order Reference ID", "value": f"`{order_id}`", "inline": True},
                {"name": "Client Identifier", "value": f"**{customer}**", "inline": True},
                {"name": "Bespoke Selection", "value": f"*{item}*", "inline": False},
                {"name": "Settlement Volume", "value": f"`{formatted_amount}` via {gateway}", "inline": True},
                {"name": "Gateway Signature Reference", "value": f"`{reference}`", "inline": True}
            ],
            "footer": {"text": "Zannie Premium Apparel Pipeline Core"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass

@zannie_bp.route('/api/orders/create', methods=['POST'])
def zannie_create_order():
    data = request.get_json() or {}
    customer_name = data.get('customer_name')
    customer_email = data.get('customer_email')
    customer_phone = data.get('customer_phone', '')
    garment_name = data.get('garment_name')
    base_price_ngn = data.get('base_price_ngn')
    
    fabric_matrix = data.get('fabric_matrix', 'Standard Blend')
    embroidery_profile = data.get('embroidery_profile', 'Standard Stitch')
    measurements = data.get('measurements_json', '{}')
    
    if not all([customer_name, customer_email, garment_name, base_price_ngn]):
        return jsonify({"status": "error", "message": "Missing required transactional fields"}), 400
        
    order_id = f"ZAN-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        conn = sqlite3.connect(ZANNIE_DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO custom_orders (order_id, customer_name, customer_email, customer_phone, garment_name, base_price_ngn) VALUES (?, ?, ?, ?, ?, ?);",
                       (order_id, customer_name, customer_email, customer_phone, garment_name, base_price_ngn))
        cursor.execute("INSERT INTO order_specifications (order_id, fabric_matrix, embroidery_profile, measurements_json) VALUES (?, ?, ?, ?);",
                       (order_id, fabric_matrix, embroidery_profile, measurements))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Order entry initialized successfully", "order_id": order_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Storage engine fault: {str(e)}"}), 500

@zannie_bp.route('/api/webhooks/payment', methods=['POST'])
def zannie_payment_webhook():
    data = request.get_json() or {}
    event = data.get('event')
    reference = data.get('reference')
    order_id = data.get('order_id')
    gateway = data.get('gateway')
    currency = data.get('currency', 'NGN')
    amount = data.get('amount')

    if event == 'charge.success' and order_id and reference:
        transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        try:
            conn = sqlite3.connect(ZANNIE_DB)
            cursor = conn.cursor()

            cursor.execute("SELECT customer_name, garment_name FROM custom_orders WHERE order_id = ?;", (order_id,))
            order_row = cursor.fetchone()
            customer_name = order_row[0] if order_row else "Unknown Customer"
            garment_name = order_row[1] if order_row else "Bespoke Apparel"

            cursor.execute("INSERT INTO transaction_logs (transaction_id, order_id, gateway, currency_code, amount_paid, gateway_reference, payment_status) VALUES (?, ?, ?, ?, ?, ?, 'Successful');",
                           (transaction_id, order_id, gateway, currency, amount, reference))
            cursor.execute("UPDATE custom_orders SET order_status = 'Processing' WHERE order_id = ?;", (order_id,))
            conn.commit()
            conn.close()
            
            dispatch_payment_webhook_alert(order_id, customer_name, garment_name, currency, amount, gateway, reference)
            return jsonify({"status": "webhook_processed", "message": "Order pipeline updated successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Webhook execution fault: {str(e)}"}), 500

    return jsonify({"status": "ignored", "message": "Invalid webhook metadata parameters"}), 400
