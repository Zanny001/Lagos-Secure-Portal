import sqlite3
import os
import time

DB_FILE = "zannie_sales.db"

def init_zannie_database():
    """
    Initializes the SQLite database for the Zannie Brand storefront.
    Creates tables for managing active checkout orders and verified payments.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Orders Table: Tracks checkouts before they are paid
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_email TEXT NOT NULL,
            amount_kobo INTEGER NOT NULL,
            currency TEXT DEFAULT 'NGN',
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL
        )
    ''')
    
    # 2. Payments Table: Logs verified successful Paystack transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verified_payments (
            paystack_reference TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            amount_paid_kobo INTEGER NOT NULL,
            gateway_response TEXT,
            verified_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[ZANNIE DB] Database tables verified/initialized cleanly.")

def create_pending_order(order_id, email, amount_kobo, currency="NGN"):
    """Inserts a fresh pending order when a customer initiates checkout."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute('''
            INSERT INTO orders (order_id, customer_email, amount_kobo, currency, status, created_at)
            VALUES (?, ?, ?, ?, 'PENDING', ?)
        ''', (order_id, email, amount_kobo, currency, timestamp))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Order ID already exists
    finally:
        conn.close()

def log_successful_payment(reference, order_id, amount_kobo, message="Approved"):
    """
    Updates the order status to 'PAID' and moves the record into verified payments.
    Executed automatically inside your secure webhook listener endpoint.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Update original order status
        cursor.execute('UPDATE orders SET status = "PAID" WHERE order_id = ?', (order_id,))
        
        # Insert into verified logs
        cursor.execute('''
            INSERT INTO verified_payments (paystack_reference, order_id, amount_paid_kobo, gateway_response, verified_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (reference, order_id, amount_kobo, message, timestamp))
        conn.commit()
        print(f"[ZANNIE DB] Payment reference {reference} successfully linked to Order {order_id}.")
        return True
    except sqlite3.Error as e:
        print(f"[ZANNIE DB ERROR] Failed to record transaction: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_zannie_database()

