import os
import csv
import psycopg2
from datetime import datetime

# Built-in secure parser: Hunts for the .env file and loads variables into memory
try:
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                # Strips spaces and any quotation marks from the URL
                os.environ[key.strip()] = val.strip().strip('"\'')
except Exception:
    pass

# Securely pull the database URL
DB_URL = os.environ.get("DATABASE_URL")

def export_to_csv():
    if not DB_URL:
        print("[-] CRITICAL: DATABASE_URL not found in environment. Export aborted.")
        return

    print("[*] Connecting to Data Warehouse...")
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Grab all property leads, ordered by newest first
        cursor.execute("""
            SELECT property_type, location, price_ngn, phone, email, source_url, created_at 
            FROM leads 
            WHERE property_type IS NOT NULL 
            ORDER BY created_at DESC
        """)
        records = cursor.fetchall()
        
        if not records:
            print("[-] No records found in the database to export.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"exports/Zannie_Premium_Leads_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Asset Profile", "Location", "Valuation (NGN)", "Phone", "Email", "Listing URL", "Timestamp"])
            writer.writerows(records)
            
        print(f"[+] SUCCESS: {len(records)} leads securely exported to {filename}")
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Export Failed: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    export_to_csv()
