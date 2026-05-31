import os
import time
import sqlite3
from datetime import datetime

# Path Configuration
DB_PATH = "academic_analytics.db"
OUTPUT_FILE = "academic_master_bak.md"

def fetch_aggregated_metrics():
    """
    Connects to the academic database and safely retrieves the latest 
    performance telemetry for all tracked students.
    """
    if not os.path.exists(DB_PATH):
        print(f"[-] Error: Database file '{DB_PATH}' not found. Run student_tracker.py first.")
        return []
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT student_name, syllabus_type, average_score, attendance_rate, last_evaluated 
            FROM student_metrics
            ORDER BY average_score DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[-] Database extraction failure: {e}")
        return []

def build_markdown_report(metrics_data):
    """
    Transforms raw relational rows into a beautifully structured, 
    studio-grade Markdown summary master document.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"""# 🎓 ZANNIE ACADEMIC MANAGEMENT SUITE: MASTER DIGEST
**Report Compilation Date:** {timestamp}  
**Lead Instructor:** Elebute Hassan Oluwafemi  
**System Status:** Verified & Synchronized  

---

## 📊 Executive Roster Summary Matrix
Below is the combined performance telemetry extracted from the active tracking database node.

| Student Name | Curriculum / Syllabus Track | Cumulative Average | Attendance Rate | Last Evaluated |
| :--- | :--- | :---: | :---: | :--- |
"""
    
    # Append structured rows dynamically
    for row in metrics_data:
        name, syllabus, avg, attendance, last_eval = row
        md_content += f"| **{name}** | {syllabus} | `{avg:.1f}%` | `{attendance:.1f}%` | {last_eval} |\n"
        
    md_content += """
---

## 📈 Contextual Performance Indicators & Benchmarks
* **Target Excellence Zone (>= 85%):** Students maintaining these marks display advanced problem-solving speed and complete execution.
* **Proficient Track (75% - 84%):** Solid momentum, displaying competence and rising structural confidence.
* **Revision Advisory (< 75%):** Target areas identified for step-by-step structural breakdowns during upcoming instruction cycles.

## 📌 Administrative Footnote
*This file is an auto-generated data export optimized for quick distribution, filing, and cross-platform verification workflows. Raw individual files remain safely cached within local filesystem nodes.*
"""
    return md_content

def main():
    print("==================================================")
    print("🚀 INITIALIZING ACADEMIC COMPILATION TOOL        ")
    print("==================================================")
    
    # 1. Harvest telemetry from database
    records = fetch_aggregated_metrics()
    if not records:
        print("[-] Aborting compile sequence: No data payload retrieved.")
        return
        
    print(f"[*] Aggregating data structures for {len(records)} active profiles...")
    
    # 2. Compile document payload
    report_md = build_markdown_report(records)
    
    # 3. Write structured document to disk
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"[SUCCESS] Master digest compiled successfully -> {OUTPUT_FILE}")
    except Exception as e:
        print(f"[-] File IO writing failure: {e}")
        
    print("==================================================")

if __name__ == "__main__":
    main()

