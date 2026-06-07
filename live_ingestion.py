import sqlite3
import os
import csv
from datetime import datetime
from config import LEADS_DB

def init_leads_database():
    """Ensures the leads database and table structure exist."""
    conn = sqlite3.connect(LEADS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            category TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def ingest_lead_batch(leads_list):
    """Inserts a batch of harvested corporate leads into the database."""
    conn = sqlite3.connect(LEADS_DB)
    cursor = conn.cursor()
    
    inserted_count = 0
    for lead in leads_list:
        # Check for duplicates based on email to keep data clean
        cursor.execute("SELECT id FROM leads WHERE email = ?", (lead['email'],))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO leads (business_name, category, email, phone, harvested_at) VALUES (?, ?, ?, ?, ?)",
                (lead['business_name'], lead['category'], lead['email'], lead['phone'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            inserted_count += 1
            
    conn.commit()
    conn.close()
    print(f"[+] Successfully ingested {inserted_count} new unique corporate leads.")

def export_to_premium_csv():
    """Generates the static CSV file that the web application serves for download."""
    csv_path = "lagos_premium_leads.csv"
    
    if not os.path.exists(LEADS_DB):
        print("[-] No database found to export.")
        return

    conn = sqlite3.connect(LEADS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT business_name, category, email, phone, harvested_at FROM leads ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Corporate Entity", "Target Sector", "Direct Email Asset", "Position / Title", "Ingestion Timestamp"])
        writer.writerows(rows)
        
    print(f"[+] Exported {len(rows)} records to local asset pipeline: {csv_path}")

if __name__ == "__main__":
    print("[*] Launching Lagos Harvester Ingestion Engine...")
    init_leads_database()
    
    # Target mock data representing standard Lagos agency/real-estate leads
    sample_harvested_data = [
        {
            "business_name": "Eko Atlantic Realty",
            "category": "Real Estate",
            "email": "info@ekoatlanticrealty.ng",
            "phone": "+2348031112222"
        },
        {
            "business_name": "Zannie Tech Agencies",
            "category": "Digital Marketing",
            "email": "devops@zannie.co",
            "phone": "+2348123334444"
        },
        {
            "business_name": "Lekki Horizon Developers",
            "category": "Real Estate",
            "email": "procurement@lekkihorizon.com",
            "phone": "+2349055556666"
        }
    ]
    
    ingest_lead_batch(sample_harvested_data)
    export_to_premium_csv()
    print("[+] Pipeline execution cycle complete.")
