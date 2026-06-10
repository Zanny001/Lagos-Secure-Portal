import sqlite3
import os
from flask import Flask, jsonify
from config import DATABASE_URL, ACADEMIC_DB, ZANNIE_DB

# Import Blueprints
from modules.academic import academic_bp
from modules.zannie import zannie_bp
from modules.harvester import harvester_bp
from modules.scholarships import scholarships_bp

app = Flask(__name__)

# ===================================================================
# DYNAMIC DATABASE RESOLUTION (SQLITE / POSTGRES HYBRID ENGINE)
# ===================================================================
def execute_init_query(db_target, sqlite_query, postgres_query):
    """Executes schema initialization depending on the targeted database connection dialect."""
    try:
        if str(db_target).startswith("postgresql://") or str(db_target).startswith("postgres://"):
            import psycopg2
            conn = psycopg2.connect(db_target)
            cursor = conn.cursor()
            cursor.execute(postgres_query)
            conn.commit()
            conn.close()
        else:
            if os.environ.get('VERCEL'):
                db_path = os.path.join('/tmp', os.path.basename(db_target))
            else:
                db_path = db_target

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sqlite_query)
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"[-] Database initialization warning for target {db_target}: {str(e)}")

# ===================================================================
# DATABASE INITIALIZATION ROUTINES
# ===================================================================
def init_all_databases():
    """Initializes schema dependencies across SQLite or PostgreSQL clusters."""

    # Academic Tables
    execute_init_query(
        ACADEMIC_DB,
        "CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT NOT NULL, subject TEXT NOT NULL, score REAL NOT NULL, record_date TEXT NOT NULL);",
        "CREATE TABLE IF NOT EXISTS grades (id SERIAL PRIMARY KEY, student_name TEXT NOT NULL, subject TEXT NOT NULL, score REAL NOT NULL, record_date TIMESTAMPTZ NOT NULL);"
    )

    execute_init_query(
        ACADEMIC_DB,
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, track TEXT NOT NULL, subject TEXT NOT NULL, max_weight INTEGER NOT NULL, deadline TEXT, content_markdown TEXT NOT NULL);",
        "CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT NOT NULL, track TEXT NOT NULL, subject TEXT NOT NULL, max_weight INTEGER NOT NULL, deadline TIMESTAMPTZ, content_markdown TEXT NOT NULL);"
    )

    # Zannie Core E-commerce Tables
    execute_init_query(
        ZANNIE_DB,
        "CREATE TABLE IF NOT EXISTS custom_orders (order_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, customer_email TEXT NOT NULL, customer_phone TEXT, garment_name TEXT NOT NULL, base_price_ngn REAL NOT NULL, order_status TEXT DEFAULT 'Pending' CHECK(order_status IN ('Pending', 'Processing', 'Dispatched', 'Completed', 'Cancelled')), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "CREATE TABLE IF NOT EXISTS custom_orders (order_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, customer_email TEXT NOT NULL, customer_phone TEXT, garment_name TEXT NOT NULL, base_price_ngn REAL NOT NULL, order_status TEXT DEFAULT 'Pending' CHECK(order_status IN ('Pending', 'Processing', 'Dispatched', 'Completed', 'Cancelled')), created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);"
    )

    execute_init_query(
        ZANNIE_DB,
        "CREATE TABLE IF NOT EXISTS order_specifications (spec_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, fabric_matrix TEXT, embroidery_profile TEXT, measurements_json TEXT, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id) ON DELETE CASCADE);",
        "CREATE TABLE IF NOT EXISTS order_specifications (spec_id SERIAL PRIMARY KEY, order_id TEXT NOT NULL, fabric_matrix TEXT, embroidery_profile TEXT, measurements_json TEXT, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id) ON DELETE CASCADE);"
    )

    execute_init_query(
        ZANNIE_DB,
        "CREATE TABLE IF NOT EXISTS transaction_logs (transaction_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, gateway TEXT NOT NULL CHECK(gateway IN ('Paystack', 'Flutterwave')), currency_code TEXT NOT NULL CHECK(currency_code IN ('NGN', 'USD', 'GBP', 'EUR')), amount_paid REAL NOT NULL, gateway_reference TEXT UNIQUE, payment_status TEXT NOT NULL CHECK(payment_status IN ('Initiated', 'Successful', 'Failed', 'Reversed')), updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id));",
        "CREATE TABLE IF NOT EXISTS transaction_logs (transaction_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, gateway TEXT NOT NULL CHECK(gateway IN ('Paystack', 'Flutterwave')), currency_code TEXT NOT NULL CHECK(currency_code IN ('NGN', 'USD', 'GBP', 'EUR')), amount_paid REAL NOT NULL, gateway_reference TEXT UNIQUE, payment_status TEXT NOT NULL CHECK(payment_status IN ('Initiated', 'Successful', 'Failed', 'Reversed')), updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id));"
    )

    print("[+] Unified operational database clusters synchronized successfully.")

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
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/v1/health", methods=["GET"])
def global_system_health():
    is_postgres = str(ACADEMIC_DB).startswith("postgres")
    return jsonify({                                                          
        "status": "online",
        "environment": "Unified Production Matrix (Cloud)" if os.environ.get('VERCEL') else "Local Staging Matrix (UserLAnd)",
        "database_layer": "Remote PostgreSQL Cluster" if is_postgres else "Local Ephemeral Storage",
        "modules_active": [
            "Academic Analytics Engine v2",                                   
            "Zannie Multi-Currency Checkout",                                 
            "Harvester Intelligence",                                         
            "Global Scholarships Matrix"
        ]                                                                     
    }), 200                                                                                                                                                 

@app.route('/favicon.ico')
def favicon():
    return "", 204

if __name__ == "__main__":                                                    
    app.run(host="0.0.0.0", port=5001, debug=True)
