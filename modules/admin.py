import os
import sqlite3
from flask import Blueprint, render_template
from config import LEADS_DB, ZANNIE_DB, ACADEMIC_DB

# ===================================================================
# MODULE A: MASTER CONTROL DASHBOARD
# ===================================================================
admin_bp = Blueprint('admin', __name__)

def get_table_count(db_path, table_name):
    """Safely queries row counts, returning 0 if the DB or table doesn't exist yet."""
    if not os.path.exists(db_path):
        return 0
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Check if table exists first to prevent execution faults
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                return 0
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
    except Exception:
        return 0

@admin_bp.route("/dev-admin", methods=["GET"])
def programmer_hub():
    """Aggregates system health and database telemetry across all modules."""
    stats = {
        "harvester_status": "ONLINE",
        "total_leads": get_table_count(LEADS_DB, 'leads'),
        
        "zannie_status": "ONLINE",
        "total_orders": get_table_count(ZANNIE_DB, 'custom_orders'),
        
        "scholarships_status": "ONLINE",
        "total_scholarships": get_table_count(ACADEMIC_DB, 'funding_opportunities'),
        
        "academic_status": "STANDBY"
    }

    # Override statuses to ERROR if connectivity fails completely
    if stats["total_leads"] == 0 and not os.path.exists(LEADS_DB):
        stats["harvester_status"] = "PENDING DATA"
    if stats["total_orders"] == 0 and not os.path.exists(ZANNIE_DB):
        stats["zannie_status"] = "PENDING DATA"
    if stats["total_scholarships"] == 0 and not os.path.exists(ACADEMIC_DB):
        stats["scholarships_status"] = "PENDING DATA"

    return render_template("master_control.html", stats=stats)
