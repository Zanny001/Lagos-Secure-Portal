import re
import sys
import json
import sqlite3
from datetime import datetime

DB_PATH = "lagos_leads.db"

# Local Registry Mock Cache for instant absolute verification checks
MOCK_CORPORATE_REGISTRY = {
    "RC123456": {"company_name": "ZANNIE LOGISTICS LTD", "status": "ACTIVE", "city": "IKEJA", "date_inc": "2021-04-12"},
    "RC789012": {"company_name": "LAGOS TRUST DIGITAL AGENCY", "status": "ACTIVE", "city": "YABA", "date_inc": "2023-09-18"},
    "RC654321": {"company_name": "ALABA HARVESTER FOODS", "status": "DISSOLVED", "city": "OJO", "date_inc": "2018-11-05"}
}

def init_verification_ledger():
    """Initializes a specific database table to store logged verification histories."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verified_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rc_number TEXT UNIQUE,
                company_name TEXT NOT NULL,
                status TEXT,
                city TEXT,
                verification_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def verify_corporate_rc(raw_rc):
    """Cleans up raw RC input, validates formats, and performs an intersection check."""
    # Strip spaces, symbols, and force uppercase
    cleaned_rc = re.sub(r"[\s\-\_\.]", "", raw_rc).upper()
    
    # Prepend 'RC' if the user only supplied numerals
    if cleaned_rc.isdigit():
        cleaned_rc = f"RC{cleaned_rc}"
        
    print(f"[PROCESS] Standardized Target String: '{cleaned_rc}'")
    
    # Enforce standard formatting regex check
    if not re.match(r"^RC\d{6,8}$", cleaned_rc):
        return {"status": "INVALID_FORMAT", "message": "RC number must follow 'RC' prefix + 6 to 8 digits."}

    # Absolute matching loop check against the registry storage block
    if cleaned_rc in MOCK_CORPORATE_REGISTRY:
        reg_info = MOCK_CORPORATE_REGISTRY[cleaned_rc]
        
        # Log valid record to database history
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO verified_companies (rc_number, company_name, status, city)
                    VALUES (?, ?, ?, ?)
                """, (cleaned_rc, reg_info["company_name"], reg_info["status"], reg_info["city"]))
                conn.commit()
        except sqlite3.Error as e:
            print(f"[DB WARN] Could not update ledger record: {e}")

        return {
            "status": "VERIFIED",
            "rc_number": cleaned_rc,
            "company_name": reg_info["company_name"],
            "registry_status": reg_info["status"],
            "location": reg_info["city"],
            "date_incorporated": reg_info["date_inc"]
        }
        
    return {"status": "NOT_FOUND", "message": "Target business registration string not recorded in active registry archives."}

if __name__ == "__main__":
    init_verification_ledger()
    
    # Grab input arguments from shell console command lines
    target_string = sys.argv[1] if len(sys.argv) > 1 else "123456"
    
    print("\n============================================================")
    print("🔒 LAGOS SECURE TRUST ENGINE — REGISTRATION CHECK PIPELINE")
    print("============================================================")
    
    result = verify_corporate_rc(target_string)
    print(json.dumps(result, indent=4))
    print("============================================================\n")
