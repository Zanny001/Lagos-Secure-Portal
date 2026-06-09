import sqlite3
import os
import sys

# Add root directory to path so it can read config.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config import ACADEMIC_DB

def add_grade():
    print("\n🎓 ZANNIE ACADEMIC GRADE ENTRY PORTAL")
    print("-----------------------------------------")
    student_name = input("Enter Student Name (e.g., Kehinde, Tooki, Demi): ").strip()
    if not student_name: return
    
    subject = input("Enter Subject/Topic (e.g., Physics Kinematics, WAEC Math): ").strip()
    try:
        score = float(input("Enter Score (Percentage, e.g., 88.5): "))
    except ValueError:
        print("❌ Invalid score format.")
        return

    record_date = input("Enter Date (YYYY-MM-DD) [Leave blank for today]: ").strip()
    if not record_date:
        from datetime import datetime
        record_date = datetime.today().strftime('%Y-%m-%d')

    try:
        conn = sqlite3.connect(ACADEMIC_DB)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO grades (student_name, subject, score, record_date)
            VALUES (?, ?, ?, ?)
        ''', (student_name, subject, score, record_date))
        conn.commit()
        conn.close()
        print(f"✅ Successfully recorded {score}% for {student_name} in {subject}!")
    except Exception as e:
        print(f"❌ Database Write Error: {e}")

if __name__ == "__main__":
    while True:
        add_grade()
        cont = input("\nAdd another record? (y/n): ").lower()
        if cont != 'y':
            break
