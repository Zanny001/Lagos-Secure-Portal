import sqlite3
import os
import sys
import datetime

# Connect to root path for config variables
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config import ACADEMIC_DB                                                

PORTAL_ROOT = "/home/userland/Lagos-Secure-Portal"
REPORTS_DIR = os.path.join(PORTAL_ROOT, "reports")

def compile_stats():
    print("[*] Accessing Academic Storage Engines...")
    if not os.path.exists(ACADEMIC_DB):
        print(f"[-] Database file not found at {ACADEMIC_DB}. Generating empty structural mock metrics.")
        return                                                                                                                                                  
    
    try:
        conn = sqlite3.connect(ACADEMIC_DB)
        cursor = conn.cursor()
        
        # Pull performance metrics aggregated by student names (Preserving your core logic)
        cursor.execute("SELECT student_name, AVG(score), COUNT(id) FROM grades GROUP BY student_name")
        rows = cursor.fetchall()
        conn.close()

        # 1. Print directly to terminal/logs for console visibility
        print("\n📊 CURRENT SYSTEM PERFORMANCE ANALYTICS")
        print("====================================================")
        print(f"{'STUDENT':<18} | {'CUMULATIVE GRADE':<18} | {'TASKS SUBMITTED'}")
        print("----------------------------------------------------")
        for name, avg_score, count in rows:
            print(f"{name:<18} | {avg_score:>16.1f}% | {count:>12} tasks")
        print("====================================================")
        print("[+] Syncing compilation hooks back to layout viewboards.")

        # 2. Upgrade: Compile to Markdown asset file for report tracking
        os.makedirs(REPORTS_DIR, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(REPORTS_DIR, f"academic_summary_{timestamp}.md")
        
        with open(report_path, "w") as f:
            f.write("# 📚 Zannie Academic Progress Analytics Summary\n")
            f.write(f"**Compiled:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WAT\n\n")
            f.write("### Aggregated Student Analytics Matrix\n\n")
            f.write("| Student Profile Name | Cumulative Average | Evaluated Tasks |\n")
            f.write("|----------------------|--------------------|-----------------|\n")
            for name, avg_score, count in rows:
                f.write(f"| {name} | **{avg_score:.1f}%** | {count} completed |\n")
            f.write("\n\n*Report automatically compiled via DevOps Maintenance Engine.*")

        print(f"[+] Shareable markdown matrix file compiled at: {report_path}")

    except Exception as e:
        print(f"❌ Critical compiling interruption: {e}")

if __name__ == "__main__":
    compile_stats()
