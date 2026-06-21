import os
import sqlite3
from functools import wraps
from flask import Blueprint, request, jsonify

# UPGRADE: Import the unified, dynamic database connection logic directly from Harvester
from modules.harvester import get_db_connection 

api_bp = Blueprint('api', __name__)

# Master API keys for paying enterprise clients
AUTHORIZED_API_KEYS = {
    "sk_live_zannie_alpha_9982": "Alpha Hedge Fund",
    "sk_live_zannie_beta_7731": "Lagos PropTech Devs"
}

def require_api_key(f):
    """Middleware to enforce strict API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if not api_key or api_key not in AUTHORIZED_API_KEYS:
            return jsonify({"status": "error", "message": "Unauthorized. Invalid or missing X-API-KEY."}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route("/v1/leads/premium", methods=["GET"])
@require_api_key
def get_premium_leads():
    """Outputs high-value real estate intel in pristine JSON format for B2B consumption."""
    client_name = AUTHORIZED_API_KEYS.get(request.headers.get("X-API-KEY"))
    
    try:
        # Utilize the exact same connection logic as the ingestion engine
        conn, is_postgres = get_db_connection()
        
        if not is_postgres:
            conn.row_factory = sqlite3.Row  # Enables column-name addressing for SQLite
            
        cursor = conn.cursor()
        
        # Universal query syntax for both SQLite and PostgreSQL
        cursor.execute("""
            SELECT id, property_type, location, price_ngn, ai_staged_image_url, created_at 
            FROM leads 
            WHERE property_type IS NOT NULL 
            ORDER BY id DESC LIMIT 100
        """)
        
        if is_postgres:
            # Map column names dynamically if using PostgreSQL
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            leads_data = [dict(zip(columns, row)) for row in rows]
        else:
            rows = cursor.fetchall()
            leads_data = [dict(row) for row in rows]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "client": client_name,
            "total_records": len(leads_data),
            "data": leads_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Data pipeline fault: {str(e)}"}), 500

