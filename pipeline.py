import sqlite3
import re

DB_PATH = "lagos_leads.db"

def init_database():
    """Initializes the background harvesting table infrastructure."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                phone_number TEXT UNIQUE,
                address TEXT,
                category TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("[HARVESTER DB] Target lead tables initialized cleanly.")

def clean_phone(phone_str):
    """
    Sanitizes raw string formats into verified West African phone numbering profiles.
    Matches standard variants: 070..., +234..., 234...
    """
    # Strips spaces, dashes, and parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_str)
    
    # Validates string format against Nigerian telecom numbering plans
    if re.match(r"^(?:\+234|234|0)[789][01]\d{8}$", cleaned):
        return cleaned
    return None

def save_leads_batch(leads_list):
    """
    Ingests an accumulated batch list of scraped business vectors.
    Uses memory buffered bulk transaction execution to optimize mobile flash I/O.
    """
    valid_leads = []
    for name, raw_phone, address, cat in leads_list:
        phone = clean_phone(raw_phone)
        if phone and name:
            valid_leads.append((name.strip(), phone, address.strip(), cat.strip()))
            
    if not valid_leads:
        return 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            # INSERT OR IGNORE safely skips matching unique phone numbers to avoid duplicates
            cursor.executemany("""
                INSERT OR IGNORE INTO business_leads (company_name, phone_number, address, category)
                VALUES (?, ?, ?, ?)
            """, valid_leads)
            conn.commit()
            return cursor.rowcount  # Returns the total number of brand-new records saved
        except sqlite3.Error as e:
            print(f"[HARVESTER DATABASE ERROR] Sync fault occurred: {e}")
            return 0

import csv  # <-- Import Python's native CSV handling library

def export_leads_to_csv(output_filename="lagos_harvested_leads.csv"):
    """
    Queries the background data tables and exports all unique business leads
    into a clean, client-ready CSV file format.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Extract items sorted sequentially by the newest entries first
            cursor.execute("SELECT id, company_name, phone_number, address, category, timestamp FROM business_leads ORDER BY id DESC")
            rows = cursor.fetchall()
            
            if not rows:
                print("[HARVESTER] No entries found in the database to export.")
                return False
                
            # Open file with explicit UTF-8 encoding and newline handling for cross-platform stability
            with open(output_filename, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ["Lead ID", "Company Name", "Phone Number", "Address", "Business Category", "Date Harvested"]
                writer = csv.writer(csv_file)
                
                # Write the header block row
                writer.writerow(fieldnames)
                
                # Stream database data rows directly into the file rows
                for row in rows:
                    writer.writerow([
                        row["id"],
                        row["company_name"],
                        row["phone_number"],
                        row["address"],
                        row["category"],
                        row["timestamp"]
                    ])
                    
            print(f"[HARVESTER] Export successful! {len(rows)} leads saved securely to: '{output_filename}'")
            return True
            
    except Exception as e:
        print(f"[HARVESTER ERROR] Failed to compile CSV export layer: {e}")
        return False

