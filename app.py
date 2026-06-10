import sqlite3
import os
from flask import Flask, jsonify
from config import ACADEMIC_DB, ZANNIE_DB

# Import Blueprints                                                           
from modules.academic import academic_bp
from modules.zannie import zannie_bp
from modules.harvester import harvester_bp
from modules.scholarships import scholarships_bp

app = Flask(__name__)                                                         

# ===================================================================
# DYNAMIC FILESYSTEM PATH RESOLUTION (VERCEL COMPATIBILITY)
# ===================================================================
# Vercel environments are read-only except for the /tmp directory.
if os.environ.get('VERCEL'):
    TARGET_ACADEMIC_DB = os.path.join('/tmp', os.path.basename(ACADEMIC_DB))
    TARGET_ZANNIE_DB = os.path.join('/tmp', os.path.basename(ZANNIE_DB))
else:
    TARGET_ACADEMIC_DB = ACADEMIC_DB
    TARGET_ZANNIE_DB = ZANNIE_DB

# ===================================================================
# DATABASE INITIALIZATION
# ===================================================================
def init_all_databases():
    """Initializes schema dependencies across operational storage clusters."""
    # 1. Academic DB
    conn_ac = sqlite3.connect(TARGET_ACADEMIC_DB)
    cursor_ac = conn_ac.cursor()
    cursor_ac.execute('''
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,                                         
        student_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        score REAL NOT NULL,                                                          
        record_date TEXT NOT NULL
    )
    ''')
    cursor_ac.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,                                         
        title TEXT NOT NULL,
        track TEXT NOT NULL,
        subject TEXT NOT NULL,
        max_weight INTEGER NOT NULL,                                                  
        deadline TEXT,
        content_markdown TEXT NOT NULL                                                
    )
    ''')
    conn_ac.commit()
    conn_ac.close()

    # 2. Zannie DB
    conn_za = sqlite3.connect(TARGET_ZANNIE_DB)                                          
    cursor_za = conn_za.cursor()
    cursor_za.execute("""
    CREATE TABLE IF NOT EXISTS custom_orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT,
        garment_name TEXT NOT NULL,
        base_price_ngn REAL NOT NULL,
        order_status TEXT DEFAULT 'Pending' CHECK(order_status IN ('Pending', 'Processing', 'Dispatched', 'Completed', 'Cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor_za.execute("""
    CREATE TABLE IF NOT EXISTS order_specifications (
        spec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        fabric_matrix TEXT,                                                           
        embroidery_profile TEXT,
        measurements_json TEXT,                                                       
        FOREIGN KEY (order_id) REFERENCES custom_orders(order_id) ON DELETE CASCADE
    );
    """)
    cursor_za.execute("""                                                         
    CREATE TABLE IF NOT EXISTS transaction_logs (                                 
        transaction_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,                                                       
        gateway TEXT NOT NULL CHECK(gateway IN ('Paystack', 'Flutterwave')),
        currency_code TEXT NOT NULL CHECK(currency_code IN ('NGN', 'USD', 'GBP', 'EUR')),                                                                           
        amount_paid REAL NOT NULL,                                                    
        gateway_reference TEXT UNIQUE,
        payment_status TEXT NOT NULL CHECK(payment_status IN ('Initiated', 'Successful', 'Failed', 'Reversed')),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES custom_orders(order_id)
    );
    """)
    conn_za.commit()                                                              
    conn_za.close()

    print(f"[+] All databases synchronized successfully at: {os.path.abspath(TARGET_ACADEMIC_DB)}")

# Run database synchronization routines before processing requests
init_all_databases()

# ===================================================================
# BLUEPRINT REGISTRATION
# ===================================================================
app.register_blueprint(academic_bp)
app.register_blueprint(zannie_bp)
app.register_blueprint(harvester_bp)
app.register_blueprint(scholarships_bp)

# ===================================================================
# SYSTEM GLOBAL HEALTH CHECK & MIDDLEWARE
# ===================================================================
@app.after_request                                                            
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"             
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/v1/health", methods=["GET"])
def global_system_health():
    return jsonify({                                                              
        "status": "online",
        "environment": "Unified Production Matrix" if os.environ.get('VERCEL') else "Local Staging Environment",                                      
        "modules_active": [
            "Academic Analytics Engine v2",                                               
            "Zannie Multi-Currency Checkout",                                             
            "Harvester Intelligence",                                                     
            "Global Scholarships Matrix"
        ]                                                                             
    }), 200                                                                                                                                                    

if __name__ == "__main__":                                                     
    app.run(host="0.0.0.0", port=5001, debug=True)

