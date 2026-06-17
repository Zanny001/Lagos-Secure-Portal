import os
import time
import sqlite3

# Persistent Database Path Configuration
DB_PATH = "academic_analytics.db"

# Your Master Data Roster Matrix (Preserved and Secured)
STUDENT_ROSTER = [
    {
        "name": "Kehinde",
        "standard": "IGCSE / WAEC Math Intensive",
        "scores": [85, 92, 78, 90],
        "attendance_pct": 100.0,
        "tutor_remarks": "Demonstrates excellent problem-solving speed. Quadratic functions masterclass completed with highly stellar performance."
    },
    {
        "name": "Tooki",
        "standard": "Year 8 Mathematics",
        "scores": [72, 68, 75, 80],
        "attendance_pct": 95.0,
        "tutor_remarks": "Steady improvement observed in algebraic fractions. Responding remarkably well to structural step-by-step breakdown techniques."
    },
    {
        "name": "Odutana Agboola",
        "standard": "OCR GCSE Physics / Math",
        "scores": [88, 84, 91, 89],
        "attendance_pct": 98.0,
        "tutor_remarks": "Outstanding analytical reasoning skills in kinematics. Consistently provides flawless mathematical derivations."
    },
    {
        "name": "Demi",
        "standard": "WAEC Mathematics Core",
        "scores": [60, 65, 74, 78],
        "attendance_pct": 92.0,
        "tutor_remarks": "Significant momentum gained over the past 3 sessions. Confidence levels in Euclidean geometry are rising nicely."
    }
]

def init_academic_db():
    """Initializes the database schema for tracking persistent tracking trends."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT UNIQUE,
            syllabus_type TEXT,
            average_score REAL,
            attendance_rate REAL,
            last_evaluated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_and_generate_reports():
    """Processes roster metrics, saves to SQLite, and compiles text report sheets."""
    timestamp = time.strftime('%Y-%m-%d')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    init_academic_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[*] Processing academic records and compiling reports...")

    for student in STUDENT_ROSTER:
        name = student["name"]
        standard = student["standard"]
        scores = student["scores"]
        attendance = student["attendance_pct"]
        remarks = student["tutor_remarks"]

        avg_score = sum(scores) / len(scores)

        # Assign structural grade boundaries
        if avg_score >= 85: grade = "A* (Excellent Execution)"
        elif avg_score >= 75: grade = "A (Highly Proficient)"
        elif avg_score >= 65: grade = "B (Solid Competence)"
        elif avg_score >= 50: grade = "C (Developing)"
        else: grade = "D (Requires Revision)"

        # 1. Database Persistent UPSERT Operation
        cursor.execute("""
            INSERT INTO student_metrics (student_name, syllabus_type, average_score, attendance_rate, last_evaluated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_name) DO UPDATE SET
                average_score = excluded.average_score,
                attendance_rate = excluded.attendance_rate,
                last_evaluated = CURRENT_TIMESTAMP
        """, (name, standard, avg_score, attendance))

        # 2. Build the Studio-Grade Text Report Document
        report_template = f"""==================================================================
                 ACADEMIC PROGRESS PERFORMANCE REPORT
==================================================================
Report Generated: {timestamp}
Tutor/Lead Instructor: Elebute Hassan Oluwafemi

STUDENT PROFILE:
------------------------------------------------------------------
Student Name:     {name}
Curriculum Track: {standard}
Attendance Rate:  {attendance}%

PERFORMANCE METRICS:
------------------------------------------------------------------
Recent Test Record: {', '.join([str(s) + '%' for s in scores])}
Cumulative Average: {avg_score:.1f}%
Assigned Grade:     {grade}

PROFESSIONAL INSTRUCTOR ASSESSMENT & REMARKS:
------------------------------------------------------------------
{remarks}

------------------------------------------------------------------
Status: Active & Tracking Established.
==================================================================
"""
        safe_filename = f"report_{name.lower().replace(' ', '_')}.txt"
        file_path = os.path.join(current_dir, safe_filename)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_template)
            print(f"[SUCCESS] Compiled report file and cached to DB: {safe_filename}")
        except Exception as e:
            print(f"[ERROR] Failed to compile report for {name}: {e}")

    conn.commit()
    conn.close()
    print("\n" + "="*65)
    print("🎓 ACADEMIC MANAGEMENT ENGINE: AUTOMATION SWEEP COMPLETE")
    print("="*65 + "\n")

if __name__ == "__main__":
    save_and_generate_reports()

