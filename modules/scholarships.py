import os
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from config import ACADEMIC_DB

# ===================================================================
# MODULE D: GLOBAL SCHOLARSHIPS ENGINE
# ===================================================================
scholarships_bp = Blueprint('scholarships', __name__)

def get_db_connection():
    """Resolves database file execution paths correctly across local and Vercel environments."""
    if os.environ.get('VERCEL'):
        db_path = os.path.join('/tmp', os.path.basename(ACADEMIC_DB))
    else:
        db_path = ACADEMIC_DB
    return sqlite3.connect(db_path)

@scholarships_bp.route('/', methods=['GET'])
def view_scholarships():
    """Renders all indexed fully funded opportunities stored in the matrix database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT institution, department, faculty_name, role_title, contact_email 
            FROM funding_opportunities 
            ORDER BY id DESC
        """)
        db_rows = cursor.fetchall()
        conn.close()

        # Parse rows cleanly into structured dictionaries for the frontend jinja variables
        leads = [
            {
                "Institution": row[0],
                "Department": row[1],
                "Faculty Name": row[2],
                "Title/Role": row[3],
                "Contact Email": row[4]
            } for row in db_rows
        ]

        return render_template("scholarships.html", leads=leads)
    except Exception as e:
        return f"Scholarships Storage Engine Connectivity Fault: {str(e)}", 500

@scholarships_bp.route('/api/ingest', methods=['POST'])
def ingest_funding_opportunity():
    """API Endpoint for background academic crawlers to transmit extracted assistantship vacancies."""
    try:
        data = request.get_json() or {}
        institution = data.get('institution')
        contact_email = data.get('contact_email')

        if not institution or not contact_email:
            return jsonify({"status": "error", "message": "Missing key parameters (institution, contact_email)"}), 400

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO funding_opportunities (institution, department, faculty_name, role_title, contact_email, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            institution, 
            data.get('department', 'General Admissions'), 
            data.get('faculty_name', 'N/A'), 
            data.get('role_title', 'Graduate Assistantship'), 
            contact_email, 
            timestamp
        ))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": f"Funding vacancy at {institution} successfully synced."}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database ingestion failure: {str(e)}"}), 500
