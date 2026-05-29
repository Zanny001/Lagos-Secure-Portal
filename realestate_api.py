import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)
DB_PATH = "realestate_analytics.db"

def fetch_db_metrics():
    """
    Queries your live SQLite database to extract the latest market intelligence.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enables column-name dictionary mapping
        cursor = conn.cursor()
        
        cursor.execute("SELECT location, average_price as price, active_listings as listings, classification as class FROM location_metrics")
        rows = cursor.fetchall()
        conn.close()
        
        # Format SQLite row arrays neatly into standard JSON objects
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[-] Database extraction failure: {e}")
        return []

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Public cross-origin network endpoint serving structured market trends.
    """
    data = fetch_db_metrics()
    response = jsonify(data)
    # Inject CORS compliance headers to allow seamless cross-origin browser fetches via your tunnels
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    print("[*] Launching Zannie Analytics Core API Engine on Port 5005...")
    app.run(host='127.0.0.1', port=5005, debug=False)

