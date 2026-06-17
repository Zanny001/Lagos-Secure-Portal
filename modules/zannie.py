import os
import uuid
import sqlite3
import requests
from flask import Blueprint, request, jsonify, render_template
from config import ZANNIE_DB, DISCORD_WEBHOOK_URL

# ===================================================================
# MODULE B: ZANNIE PREMIUM APPAREL BLUEPRINT
# ===================================================================
zannie_bp = Blueprint('zannie', __name__)

def get_db_connection():
    """Resolves database file execution paths correctly across local and Vercel environments."""
    if os.environ.get('VERCEL'):
        db_path = os.path.join('/tmp', os.path.basename(ZANNIE_DB))
    else:
        db_path = ZANNIE_DB
    return sqlite3.connect(db_path)

def dispatch_payment_webhook_alert(order_id, customer, item, currency, amount, gateway, reference):
    """Transmits high-priority transaction logs instantly to your Discord Operations channel."""
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

@zannie_bp.route('/dashboard', methods=['GET'])
def zannie_dashboard():
    """Serves the isolated administrative tracking interface for Zannie Fashion sales."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.order_id, o.customer_name, o.customer_email, o.garment_name, o.base_price_ngn, o.order_status, s.fabric_matrix
            FROM custom_orders o
            LEFT JOIN order_specifications s ON o.order_id = s.order_id
            ORDER BY o.created_at DESC
        """)
        orders = cursor.fetchall()
        conn.close()
        return render_template("zannie.html", orders=orders)
    except Exception as e:
        return f"Zannie Data Engine Error: {str(e)}", 500

@zannie_bp.route('/api/orders/create', methods=['POST'])
def zannie_create_order():
    """API endpoint to instantiate customer bespoke apparel records."""
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO custom_orders (order_id, customer_name, customer_email, customer_phone, garment_name, base_price_ngn) 
            VALUES (?, ?, ?, ?, ?, ?);
        """, (order_id, customer_name, customer_email, customer_phone, garment_name, base_price_ngn))
        
        cursor.execute("""
            INSERT INTO order_specifications (order_id, fabric_matrix, embroidery_profile, measurements_json) 
            VALUES (?, ?, ?, ?);
        """, (order_id, fabric_matrix, embroidery_profile, str(measurements)))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Order entry initialized successfully", "order_id": order_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Storage engine fault: {str(e)}"}), 500

@zannie_bp.route('/api/webhooks/payment', methods=['POST'])
def zannie_payment_webhook():
    """Fault-tolerant processing pipeline handling incoming webhook telemetry from Paystack / Flutterwave."""
    payload = request.get_json() or {}
    
    # Handle direct testing keys or deep structural payloads safely
    event = payload.get('event')
    reference = payload.get('reference') or payload.get('data', {}).get('reference')
    order_id = payload.get('order_id') or payload.get('data', {}).get('metadata', {}).get('order_id')
    gateway = payload.get('gateway', 'Paystack')
    currency = payload.get('currency') or payload.get('data', {}).get('currency', 'NGN')
    amount = payload.get('amount') or payload.get('data', {}).get('amount')

    # Convert gateway subunits (kobo/cents) if applicable from raw webhooks
    if amount and isinstance(amount, int) and amount > 50000:
        amount = amount / 100

    if order_id and reference:
        transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT customer_name, garment_name FROM custom_orders WHERE order_id = ?;", (order_id,))
            order_row = cursor.fetchone()
            customer_name = order_row[0] if order_row else "Unknown Customer"
            garment_name = order_row[1] if order_row else "Bespoke Apparel"
            
            cursor.execute("""
                INSERT INTO transaction_logs (transaction_id, order_id, gateway, currency_code, amount_paid, gateway_reference, payment_status) 
                VALUES (?, ?, ?, ?, ?, ?, 'Successful');
            """, (transaction_id, order_id, gateway, currency, amount, reference))
            
            cursor.execute("UPDATE custom_orders SET order_status = 'Processing' WHERE order_id = ?;", (order_id,))
            
            conn.commit()
            conn.close()
            
            dispatch_payment_webhook_alert(order_id, customer_name, garment_name, currency, amount, gateway, reference)
            return jsonify({"status": "webhook_processed", "message": "Order pipeline updated successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Webhook execution fault: {str(e)}"}), 500
            
    return jsonify({"status": "ignored", "message": "Invalid webhook metadata parameters"}), 400
