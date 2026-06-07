import sqlite3

def initialize_database():
    """
    Creates the necessary tables and unique constraints inside 
    realestate_analytics.db to ensure data persistence and valid upserts.
    """
    db_name = "realestate_analytics.db"
    print(f"Initializing SQLite database schema: {db_name}")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 1. Create raw listings historical data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            price REAL NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create optimized cache summary table with a UNIQUE constraint on location
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_summary (
            location TEXT PRIMARY KEY,
            total_listings INTEGER NOT NULL,
            average_price_ngn REAL NOT NULL,
            last_updated TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Database structure built. Ready for data ingestion ingestion.")

if __name__ == "__main__":
    initialize_database()

