import psycopg2
from config import DATABASE_URL

def initialize_database():
    print("Connecting to live Supabase PostgreSQL cluster...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 1. Create raw listings historical data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id SERIAL PRIMARY KEY,
                location TEXT NOT NULL,
                price REAL NOT NULL,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. Create the missing leads table requested by the harvester pipeline
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                property_type TEXT NOT NULL,
                location TEXT NOT NULL,
                price_ngn REAL NOT NULL,
                contact_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 3. Create optimized cache summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_summary (
                location TEXT PRIMARY KEY,
                total_listings INTEGER NOT NULL,
                average_price_ngn REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("[SUCCESS] Complete PostgreSQL schemas deployed. Ready for ingestion.")

    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")

if __name__ == "__main__":
    initialize_database()
