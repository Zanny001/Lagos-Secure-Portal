import sqlite3
import os

# Ensure this matches your config.py ZANNIE_DB path. Defaulting to local db directory.
DB_DIR = "database"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "zannie_production.db")

def initialize_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"[*] Initializing Zannie Data Matrix at: {DB_PATH}")

    # Table: Custom Orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT,
            garment_name TEXT NOT NULL,
            base_price_ngn REAL NOT NULL,
            order_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Table: Order Specifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_specifications (
            spec_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            fabric_matrix TEXT,
            embroidery_profile TEXT,
            measurements_json TEXT,
            FOREIGN KEY(order_id) REFERENCES custom_orders(order_id)
        );
    """)

    # Table: Transaction Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_logs (
            transaction_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            gateway TEXT,
            currency_code TEXT,
            amount_paid REAL,
            gateway_reference TEXT,
            payment_status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(order_id) REFERENCES custom_orders(order_id)
        );
    """)

    conn.commit()
    conn.close()
    print("[SUCCESS] Zannie Apparel schema fully deployed.")

if __name__ == "__main__":
    initialize_schema()
