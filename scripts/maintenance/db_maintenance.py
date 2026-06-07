import sqlite3
import os
import shutil
from datetime import datetime

# Path Configurations
TARGET_DATABASES = ["zannie_sales.db", "lagos_leads.db"]
BACKUP_DIR = "./backups"

def run_database_maintenance():
    print(f"==========================================================")
    print(f"🧹 STARTING AUTOMATED DATABASE MAINTENANCE & BACKUP SYSTEM")
    print(f"==========================================================")
    
    # Create the backup directory structure if missing
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"[SYSTEM] Created secure backup repository directory folder.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for db_file in TARGET_DATABASES:
        if not os.path.exists(db_file):
            print(f"[SKIP] Database target file '{db_file}' not found. Skipping entry.")
            continue

        print(f"\n⚙️ Processing Target: {db_file}")
        
        try:
            # 1. Structural Integrity Check Pass
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()[0]
                
                if result != "ok":
                    print(f"❌ [CRITICAL FAULT] Database '{db_file}' failed integrity check: {result}")
                    continue
                print(f"  ✅ Integrity Check Verified: Clean Structural Layout.")

                # 2. Performance Re-indexing and Optimization
                print(f"  ⚡ Running Optimizer Layouts (ANALYZE & VACUUM)...")
                cursor.execute("PRAGMA optimize;")
                cursor.execute("VACUUM;")
                conn.commit()
                print(f"  ✅ File Compression Complete. Storage footprints minimized.")

            # 3. Live Hot Backup Extraction Loop
            backup_filename = f"{os.path.splitext(db_file)[0]}_{timestamp}.db"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            # Use SQLite's dedicated backup API to cleanly clone data structures safely in-flight
            with sqlite3.connect(db_file) as src, sqlite3.connect(backup_path) as bck:
                src.backup(bck)
                
            print(f"  💾 Hot Backup Snapshot Created Securely -> '{backup_path}'")

        except Exception as e:
            print(f"❌ [MAINTENANCE FAULT] Optimization cycle broke for '{db_file}': {e}")

    print(f"\n==========================================================")
    print(f"✅ SYSTEM COMPRESSION AND MAINTENANCE SEQUENCE COMPLETED")
    print(f"==========================================================")

if __name__ == "__main__":
    run_database_maintenance()

