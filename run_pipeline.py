import sqlite3
import os

DB_NAME = 'realestate_analytics.db'

def insert_and_sync_lead(property_type, location, price_ngn, contact_info):
    """
    Inserts a new property record into the ledger and immediately updates
    the localized aggregate cache metrics for that specific location.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, DB_NAME)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Insert the raw property listing details
        cursor.execute('''
            INSERT INTO leads (property_type, location, price_ngn, contact_info)
            VALUES (?, ?, ?, ?)
        ''', (property_type, location, price_ngn, contact_info))
        
        print(f"[INGEST] Logged: {property_type} in {location} for ₦{price_ngn:,.2f}")
        
        # 2. Re-calculate metrics for this location to refresh the summary cache
        cursor.execute('''
            SELECT COUNT(*), AVG(price_ngn) 
            FROM leads 
            WHERE location = ?
        ''', (location,))
        total_listings, average_price = cursor.fetchone()
        
        # 3. Upsert the results into the analytics_summary table
        cursor.execute('''
            INSERT INTO analytics_summary (location, average_price_ngn, total_listings, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(location) DO UPDATE SET
                average_price_ngn = excluded.average_price_ngn,
                total_listings = excluded.total_listings,
                updated_at = CURRENT_TIMESTAMP
        ''', (location, average_price, total_listings))
        
        conn.commit()
        print(f"[SYNC] Analytics cache refreshed cleanly for: {location}")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"[PIPELINE ERROR] Transaction rolled back: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Simulating fresh inbound scraper data pipeline activity...\n")
    
    # Feeding structural test listing components into your database
    insert_and_sync_lead('5 Bedroom Fully Detached Duplex', 'Ikoyi, Lagos', 250000000.0, 'ikoyi_broker@zannie.com')
    insert_and_sync_lead('3 Bedroom Apartment', 'Lekki, Lagos', 65000000.0, 'lekki_rentals@zannie.com')
    insert_and_sync_lead('Office Space Block', 'Ikeja, Lagos', 180000000.0, 'mainland_commercial@zannie.com')
    insert_and_sync_lead('Penthouse Suite', 'Ikoyi, Lagos', 450000000.0, 'vip_luxury@zannie.com')

