import psycopg2
import os
import requests
from config import DATABASE_URL

def send_discord_alert(location, property_type, price):
    """Fires a real-time alert to the configured Discord channel."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return
        
    message = f"🚨 **New Lead Captured!**\n**Property:** {property_type}\n**Location:** {location}\n**Price:** ₦{price:,.2f}"
    
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        print(f"[ALERT ERROR] Failed to send webhook: {e}")

def insert_and_sync_lead(property_type, location, price_ngn, contact_info):
    """
    Inserts a new property record into Supabase PostgreSQL, updates the 
    aggregate cache metrics, and triggers a Discord notification.
    """
    conn_string = os.getenv("DATABASE_URL", DATABASE_URL)
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # 1. Insert raw listing
        cursor.execute('''
            INSERT INTO leads (property_type, location, price_ngn, contact_info)
            VALUES (%s, %s, %s, %s)
        ''', (property_type, location, price_ngn, contact_info))

        print(f"[INGEST] Logged: {property_type} in {location} for ₦{price_ngn:,.2f}")

        # 2. Re-calculate metrics
        cursor.execute('''
            SELECT COUNT(*), AVG(price_ngn) FROM leads WHERE location = %s
        ''', (location,))
        total_listings, average_price = cursor.fetchone()

        # 3. Upsert into analytics_summary
        cursor.execute('''
            INSERT INTO analytics_summary (location, average_price_ngn, total_listings, last_updated)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT(location) DO UPDATE SET
                average_price_ngn = EXCLUDED.average_price_ngn,
                total_listings = EXCLUDED.total_listings,
                last_updated = CURRENT_TIMESTAMP
        ''', (location, average_price, total_listings))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[SYNC] Analytics cache refreshed cleanly for: {location}")
        
        # 4. Trigger the Discord notification
        send_discord_alert(location, property_type, price_ngn)

    except Exception as e:
        print(f"[PIPELINE ERROR] Transaction rolled back: {e}")

if __name__ == "__main__":
    print("Simulating fresh inbound scraper data pipeline activity...\n")

    insert_and_sync_lead('Luxury Villa', 'Banana Island, Lagos', 850000000.0, 'banana_exclusive@zannie.com')
