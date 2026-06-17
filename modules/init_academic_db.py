import sqlite3
import os

DB_PATH = "/home/userland/Lagos-Secure-Portal/academic_stats.db"

def setup_academic_matrix():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Core table for student roster
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            gender TEXT,
            program_track TEXT
        )
    ''')

    # Assessment tracking table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            topic TEXT,
            score REAL,
            total_marks REAL,
            standard TEXT,
            assessment_date TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')

    # Seeding the initial student roster
    roster = [
        ("Kehinde", "N/A", "IGCSE/WAEC"),
        ("Tooki", "N/A", "IGCSE/WAEC"),
        ("Odutana Agboola", "F", "IGCSE/WAEC"),
        ("Demi", "N/A", "IGCSE/WAEC")
    ]
    
    c.executemany('''
        INSERT OR IGNORE INTO students (name, gender, program_track) 
        VALUES (?, ?, ?)
    ''', roster)
    
    conn.commit()
    conn.close()
    print("Path G: Zannie Academic Performance database initialized and seeded successfully in modules/.")

if __name__ == "__main__":
    setup_academic_matrix()
