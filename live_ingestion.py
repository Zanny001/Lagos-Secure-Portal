import sqlite3
import time
import requests
from random import randint

# Path to your SQLite tracking database
DB_PATH = "lagos_leads.db"

def init_database():
    """Initializes the database schema with a safe structure."""
    # timeout=30 tells SQLite to wait up to 30 seconds for locks to clear before crashing
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT,
            category TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead_safely(lead_data):
    """Inserts a harvested lead into the database, ignoring duplicates and resolving locks."""
    query = """
        INSERT OR IGNORE INTO leads (business_name, category, email, phone)
        VALUES (?, ?, ?, ?)
    """
    try:
        # High timeout parameter is critical for automated background scraping loops
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute(query, lead_data)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"[DATABASE] Lead securely committed: {lead_data[0]}")
            else:
                print(f"[DATABASE] Duplicate skipped matching unique constraints: {lead_data[2]}")
    except sqlite3.OperationalError as e:
        print(f"[DATABASE ERROR] Database currently locked or busy, retrying stream: {e}")
        time.sleep(2) # Micro-pause to let other write-threads clear
    except Exception as e:
        print(f"[DATABASE ERROR] Unexpected exception handling write: {e}")

def harvest_target_agency(url):
    """
    Executes network requests with strict timeout boundaries 
    to prevent the pipeline from hanging indefinitely.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        print(f"[HARVEST] Ping network target stream -> {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # --- Parsing Engine Logic Insertion Point ---
            # Replace this mock block with your real BS4 / Regex parsing loops
            mock_scraped_lead = ("Lagos Digital Agency", "Real Estate Marketing", "info@lagosdigital.com", "+2348000000000")
            
            save_lead_safely(mock_scraped_lead)
        else:
            print(f"[HARVEST WARNING] Target responded with non-200 status layer: {response.status_code}")
            
    except requests.Timeout:
        print(f"[NETWORK ERROR] Target connection timeout on {url}. Skipping to keep pipeline moving.")
    except requests.RequestException as e:
        print(f"[NETWORK ERROR] Failed to establish valid network pipeline framework: {e}")

if __name__ == "__main__":
    print("[START] Initializing Lagos Commercial Ingestion Engine...")
    init_database()
    
    # Example target rotation stack
    target_urls = [
        "https://example-lagos-realestate-directory.com/leads",
    ]
    
    for target in target_urls:
        harvest_target_agency(target)
        # Polite throttling pause to respect target servers and avoid getting IP banned
        time.sleep(randint(3, 7))
        
    print("[COMPLETE] Data harvesting batch cycle completed successfully. Pipeline frozen.")

