import os                                                    
import time                                                  
import sqlite3                                               
import subprocess                                            
from functools import wraps                                  
from flask import Blueprint, render_template, jsonify, request, Response                                                  
from config import LEADS_DB, ZANNIE_DB, ACADEMIC_DB          

# ===================================================================                                                     
# MODULE A: MASTER CONTROL DASHBOARD & DEVOPS PLANE
# ===================================================================                                                     
admin_bp = Blueprint('admin', __name__)
                                                             
LOG_FILE_PATH = "daemon_runtime.log"

# --- SECURITY LAYER ---
def check_auth(username, password):
    """Verifies against environment variables or falls back to default dev credentials."""
    admin_user = os.environ.get("ADMIN_USER", "root")            
    admin_pass = os.environ.get("ADMIN_PASS", "zannie2026")
    return username == admin_user and password == admin_pass
                                                             
def authenticate():
    """Sends a 401 response that enables basic auth."""
    return Response(
    'RESTRICTED SECTOR.\nAccess requires verified administrative credentials.', 401,
    {'WWW-Authenticate': 'Basic realm="Zannie Master Control Node"'})
                                                             
def requires_auth(f):
    @wraps(f)                                                    
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated                                                                                                      

# --- DATABASE TELEMETRY ---
def get_table_count(db_path, table_name):
    """Safely queries row counts, returning 0 if the DB or table doesn't exist yet."""
    if not os.path.exists(db_path):                                  
        return 0
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()                                       
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                return 0
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
    except Exception:
        return 0                                             

# --- ROUTES ---                                             
@admin_bp.route("/dev-admin", methods=["GET"])               
@requires_auth
def programmer_hub():
    """Aggregates system health and database telemetry across all modules."""
    stats = {                                                        
        "harvester_status": "ONLINE",                                
        "total_leads": get_table_count(LEADS_DB, 'leads'),
        "zannie_status": "ONLINE",
        "total_orders": get_table_count(ZANNIE_DB, 'custom_orders'),
        "scholarships_status": "ONLINE",
        "total_scholarships": get_table_count(ACADEMIC_DB, 'funding_opportunities'),
        "academic_status": "STANDBY",
        "ai_studio_status": "ONLINE", # UPGRADE: AI Telemetry
        "total_ai_assets": get_table_count(ZANNIE_DB, 'ai_gallery') # Assumes gallery lives in Zannie DB
    }

    if stats["total_leads"] == 0 and not os.path.exists(LEADS_DB):                                                                
        stats["harvester_status"] = "PENDING DATA"
    if stats["total_orders"] == 0 and not os.path.exists(ZANNIE_DB):                                                              
        stats["zannie_status"] = "PENDING DATA"
    if stats["total_scholarships"] == 0 and not os.path.exists(ACADEMIC_DB):                                                      
        stats["scholarships_status"] = "PENDING DATA"
    if stats["total_ai_assets"] == 0:
        stats["ai_studio_status"] = "AWAITING ASSETS"
                                                                 
    return render_template("admin_dashboard.html", stats=stats)                                                                                                                        

@admin_bp.route("/dev-admin/action/<action>", methods=["POST"])
@requires_auth                                               
def run_devops_action(action):
    """Securely triggers server-side shell commands from the UI."""
    # Whitelist of strictly permitted commands
    actions = {                                                      
        "ignite_scraper": f"nohup python3 -u scripts/scrapers/crawler_daemon.py > {LOG_FILE_PATH} 2>&1 &",
        "force_export": f"python3 scripts/export_leads_csv.py >> {LOG_FILE_PATH} 2>&1",                                           
        "pull_git": f"git pull origin main >> {LOG_FILE_PATH} 2>&1",
        "restart_server": "pkill -f 'flask run' || pkill -f 'python3 app.py'"
    }                                                                                                                         
    
    if action not in actions:
        return jsonify({"status": "error", "message": "Unrecognized execution protocol."}), 400
                                                                 
    try:
        # Popen executes the command in the background without freezing the Flask server
        subprocess.Popen(actions[action], shell=True)
        return jsonify({"status": "success", "message": f"Execution initialized: {action}"})                                  
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500                                                                                                                    

# --- REAL-TIME STREAMING PIPELINE (SSE) ---
@admin_bp.route("/dev-admin/stream-logs")                    
@requires_auth                                               
def stream_logs():
    """Generates a text/event-stream connection pipeline reading runtime system data logs."""
    def generate_log_stream():                                       
        # Touch or verify target file existence
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "w") as f:                              
                f.write("[SYSTEM INITIALIZED] Log stream pipeline listener mounted.\n")
                                                                     
        with open(LOG_FILE_PATH, "r") as log_file:                       
            # Catch up immediately on the last 15 lines of historic runtime data                                                      
            lines = log_file.readlines()                                 
            for line in lines[-15:]:
                yield f"data: {line}\n\n"                                                                                             
            
            # Continuous tail loop structure using the correct uppercase OS constant                                                  
            log_file.seek(0, os.SEEK_END)                                
            while True:                                                      
                line = log_file.readline()                                   
                if not line:
                    time.sleep(0.4) # Micro-sleep frame to maintain optimal CPU overhead inside UserLAnd
                    continue                                                 
                yield f"data: {line}\n\n"

    return Response(generate_log_stream(), mimetype="text/event-stream")
