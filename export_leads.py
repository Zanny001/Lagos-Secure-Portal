import sqlite3
import csv
import os
import zipfile
from datetime import datetime

LEADS_DB = "lagos_leads.db"
EXPORT_DIR = "./exports"

def export_leads_to_csv():
    print("==========================================================")
    print("📊 INITIALIZING FAULT-TOLERANT DATA EXPORT PIPELINE")
    print("==========================================================")
    
    if not os.path.exists(LEADS_DB):
        print(f"❌ [DATA FAULT] Database file '{LEADS_DB}' was not found.")
        return

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"[SYSTEM] Created secure export directory folder.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"harvested_leads_{timestamp}.csv"
    zip_filename = f"harvested_leads_{timestamp}.zip"
    
    csv_path = os.path.join(EXPORT_DIR, csv_filename)
    zip_path = os.path.join(EXPORT_DIR, zip_filename)

    try:
        print(f"[PROCESS] Streaming data points from structural tables...")
        with sqlite3.connect(LEADS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, company_name, phone_number, address, category, timestamp 
                FROM business_leads 
                ORDER BY id ASC;
            """)
            all_records = cursor.fetchall()
            
            if not all_records:
                print("⚠️ [EMPTY TABLE] No business records available to extract. Aborting.")
                return

            # Step 1: Write data cleanly to a temporary CSV file
            with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Lead ID", "Company Name", "Phone Number", "Business Address", "Market Category", "Harvested Date"])
                
                for row in all_records:
                    writer.writerow([
                        row[0],
                        row[1].strip() if row[1] else "",
                        row[2],
                        row[3].strip() if row[3] else "",
                        row[4].strip() if row[4] else "",
                        row[5]
                    ])

        # Step 2: Dynamically compress the CSV file into a ZIP archive
        print(f"[COMPRESSION] Packing data stream into a secure binary archive format...")
        with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(csv_path, arcname=csv_filename)

        # Step 3: Delete the loose uncompressed temporary CSV file to save space
        if os.path.exists(csv_path):
            os.remove(csv_path)

        print(f"==========================================================")
        print(f"✅ DATA ARCHIVING PIPELINE COMPLETION SUCCESSFUL")
        print(f"💾 Compressed File Saved -> '{zip_path}'")
        print(f"==========================================================")

    except (sqlite3.Error, IOError) as e:
        print(f"❌ [CRITICAL FAULT] Extraction processing failure: {e}")

if __name__ == "__main__":
    export_leads_to_csv()

