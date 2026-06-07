import sqlite3
import os

def initialize_real_estate_pipeline():
    """
    Initializes the SQLite database architecture for the Zannie Real Estate Harvester.
    Establishes indexing structures optimized for the Lagos commercial ecosystem.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'realestate_analytics.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create the Core Leads Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_type TEXT NOT NULL,
            location TEXT NOT NULL,
            price_ngn REAL NOT NULL,
            contact_info TEXT,
            harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create the Analytics Cache Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_summary (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT UNIQUE NOT NULL,
            average_price_ngn REAL NOT NULL,
            total_listings INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Build an Index on Location to speed up regional queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_leads_location ON leads(location)
    ''')
    
    conn.commit()
    print(f"[DATABASE SUCCESS] Database core structure built at: {db_path}")
    
    # 4. Seed an initial sample record to verify data integrity
    cursor.execute('''
        SELECT COUNT(*) FROM leads WHERE location = 'Lekki, Lagos'
    ''')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO leads (property_type, location, price_ngn, contact_info)
            VALUES ('4 Bedroom Terrace', 'Lekki, Lagos', 85000000.0, 'agent_zannie@sales.com')
        ''')
        conn.commit()
        print("[DATABASE SEED] Successfully inserted initial Lagos real estate tracking record.")
        
    conn.close()

if __name__ == "__main__":
    initialize_real_estate_pipeline()

