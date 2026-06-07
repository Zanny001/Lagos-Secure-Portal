import sqlite3

DB_PATH = "zannie_sales.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS successful_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                reference TEXT UNIQUE NOT NULL,
                notification_sent INTEGER DEFAULT 0, -- 0 = Pending, 1 = Sent Safely
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("[DATABASE] Initialization verified cleanly. Core tables ready.")

def record_sale(email, amount, currency, reference):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO successful_payments (email, amount, currency, reference)
                VALUES (?, ?, ?, ?)
            """, (email.strip().lower(), amount, currency.upper(), reference.strip()))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Ingestion sync fault occurred: {e}")
            return False

def update_notification_flag(reference):
    """Marks an order notification status as successfully dispatched."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE successful_payments 
            SET notification_sent = 1 
            WHERE reference = ?
        """, (reference,))
        conn.commit()

def fetch_all_sales():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM successful_payments ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

