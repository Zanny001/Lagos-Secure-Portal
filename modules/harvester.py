import os
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, send_file
from config import LEADS_DB

# ===================================================================
# MODULE C: LAGOS HARVESTER BLUEPRINT
# ===================================================================
harvester_bp = Blueprint('harvester', __name__)

@harvester_bp.route("/leads", methods=["GET"])
def view_harvested_leads():
    try:
        if not os.path.exists(LEADS_DB):
            return render_template("harvester.html", leads=[])
            
        conn = sqlite3.connect(LEADS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT business_name, category, email, phone, harvested_at FROM leads ORDER BY id DESC")
        leads_data = cursor.fetchall()
        conn.close()
        
        return render_template("harvester.html", leads=leads_data)
        
    except Exception as e:
        return f"Database connectivity fault: {e}", 500

@harvester_bp.route("/leads/download", methods=["GET"])
def download_leads_csv():
    """Serves the generated CSV lead pack directly to the user's local machine."""
    csv_path = "lagos_premium_leads.csv"
    if os.path.exists(csv_path):
        return send_file(
            csv_path, 
            as_attachment=True, 
            download_name=f"zannie_leads_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    else:
        return "CSV file not generated yet. Please run live_ingestion.py first.", 404
