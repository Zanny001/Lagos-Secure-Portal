import os
import sqlite3
from flask import Flask, jsonify
import json

app = Flask(__name__)

# Master Database Paths
REALESTATE_DB = "realestate_analytics.db"
ACADEMIC_DB = "academic_analytics.db"

def query_database(db_path, query, args=()):
    """Safely handles connections and extracts rows from target SQLite database nodes."""
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enables column-name dictionary mapping
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[-] Database query failure on {db_path}: {e}")
        return []

# ==============================================================================
# GLOBAL CORS MIDDLEWARE INFRASTRUCTURE
# ==============================================================================
@app.after_request
def apply_global_cors_headers(response):
    """Injects CORS compliance headers to allow seamless cross-origin traffic via public tunnels."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Bypass-Tunnel-Reminder"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response

# ==============================================================================
# ENDPOINT PATHWAY ROUTES
# ==============================================================================
@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Public cross-origin network endpoint serving structured market trends.
    Preserves original table structure: location_metrics.
    """
    query = "SELECT location, average_price as price, active_listings as listings, classification as class FROM location_metrics"
    data = query_database(REALESTATE_DB, query)
    
    # Fallback placeholder matrix if real estate database is temporarily unseeded
    if not data:
        return jsonify([
            {"location": "Lekki Phase 1 Sector", "price": 125000000.0, "listings": 14, "class": "Premium Residential"},
            {"location": "Alaba International Segment", "price": 45000000.0, "listings": 28, "class": "Commercial Hub"}
        ])
    return jsonify(data)

@app.route('/api/students', methods=['GET'])
def get_student_metrics():
    """
    Public endpoint serving unified academic telemetry metrics from the tracking node.
    """
    query = "SELECT student_name, syllabus_type, average_score, attendance_rate FROM student_metrics"
    rows = query_database(ACADEMIC_DB, query)
    
    if rows is None:
        return jsonify({"error": "Academic tracker database node unseeded or unreachable"}), 404
        
    payload = []
    for row in rows:
        payload.append({
            "name": row["student_name"],
            "track": row["syllabus_type"],
            "average": row["average_score"],
            "attendance": row["attendance_rate"]
        })
    return jsonify(payload)

@app.route('/', methods=['GET'])
def root_status_index():
    """Server entry configuration validating network layer health status."""
    return jsonify({
        "status": "online",
        "node_owner": "Elebute Hassan Oluwafemi",
        "active_endpoints": ["/api/metrics", "/api/students"]
    })


@app.route('/api/syllabus', methods=['GET'])
def get_syllabus_manifest():
    try:
        with open('lessons_manifest.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        response = jsonify(data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
    except Exception as e:
        response = jsonify({"status": "error", "message": str(e)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

if __name__ == '__main__':
    print("[*] Launching Zannie Analytics Core Unified API Engine on Port 5005...")
    # Bound to 0.0.0.0 so your localtunnel can easily forward the server external traffic
    app.run(host='0.0.0.0', port=5005, debug=False)

