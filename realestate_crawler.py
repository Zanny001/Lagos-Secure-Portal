import os
import time
import json
import sqlite3
import random

# Core Database Path Configuration
DB_PATH = "realestate_analytics.db"

def initialize_database():
    """
    Ensures that the target SQLite schema matches our data model exactly,
    building a robust schema for tracking structured real estate metrics.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the data storage table if it does not already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS location_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT UNIQUE,
            average_price REAL,
            active_listings INTEGER,
            classification TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Pre-seed the system with baseline records if the table is empty
    cursor.execute("SELECT COUNT(*) FROM location_metrics")
    if cursor.fetchone()[0] == 0:
        initial_seeds = [
            ("Lekki Phase 1 Sector", 125000000.0, 14, "Premium Residential"),
            ("Alaba International Segment", 45000000.0, 28, "Commercial Hub"),
            ("Ikeja GRA Block", 95000000.0, 9, "Premium Residential"),
            ("VGC Waterfront Sector", 150000000.0, 6, "High-End Estate")
        ]
        cursor.executemany("""
            INSERT INTO location_metrics (location, average_price, active_listings, classification)
            VALUES (?, ?, ?, ?)
        """, initial_seeds)
        conn.commit()
        print("[+] Real estate metrics table initialized and seeded with baseline rows.")
    
    conn.close()

def simulate_and_parse_crawler_feed():
    """
    Simulates a live data harvest run over your target real estate sectors.
    In full production, this loop parses raw HTML/JSON streams from your web scraper.
    """
    print("[*] Initiating web crawler loop... Extracting target market records.")
    
    # Target updates with slight micro-market price and listing variations
    updates = [
        {"location": "Lekki Phase 1 Sector", "price_mod": random.randint(-1500000, 2000000), "listing_mod": random.randint(-1, 2)},
        {"location": "Alaba International Segment", "price_mod": random.randint(-500000, 1200000), "listing_mod": random.randint(-2, 3)},
        {"location": "Ikeja GRA Block", "price_mod": random.randint(-1000000, 1500000), "listing_mod": random.randint(-1, 1)},
        {"location": "VGC Waterfront Sector", "price_mod": random.randint(-2000000, 3000000), "listing_mod": random.randint(0, 2)}
    ]
    return updates

def save_leads_to_database(raw_leads):
    """
    Commits harvested leads into the SQLite database engine using UPSERT
    syntax to safely overwrite existing entries or add new ones without conflicts.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for lead in raw_leads:
        # Fetch current historical baseline to apply modifications safely
        cursor.execute("SELECT average_price, active_listings, classification FROM location_metrics WHERE location = ?", (lead["location"],))
        record = cursor.fetchone()
        
        if record:
            current_price, current_listings, classification = record
            new_price = max(10000000, current_price + lead["price_mod"])
            new_listings = max(1, current_listings + lead["listing_mod"])
            
            # Execute transactional UPSERT block
            cursor.execute("""
                INSERT INTO location_metrics (location, average_price, active_listings, classification, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(location) DO UPDATE SET
                    average_price = excluded.average_price,
                    active_listings = excluded.active_listings,
                    last_updated = CURRENT_TIMESTAMP
            """, (lead["location"], new_price, new_listings, classification))
            
            print(f"[✏️ DB Sync] {lead['location']} -> Price: ₦{new_price:,.2f} | Listings: {new_listings}")
            
    conn.commit()
    conn.close()

def main():
    print("==================================================")
    print("🚀 ZANNIE HARVESTER PIPELINE DATABASE CONNECTOR  ")
    print("==================================================")
    
    # 1. Align schema and memory buffers
    initialize_database()
    
    # 2. Run parsing cycle execution
    harvested_data = simulate_and_parse_crawler_feed()
    
    # 3. Stream parsed objects to database tables
    save_leads_to_database(harvested_data)
    print("==================================================")
    print("[+] Database update loop complete. Pipeline synchronization successful.")

if __name__ == "__main__":
    main()

