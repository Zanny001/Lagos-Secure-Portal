from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'realestate_analytics.db'

def get_data_from_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, DB_NAME)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Selecting columns explicitly using last_updated to match the db schema
    cursor.execute('SELECT location, total_listings, average_price_ngn, last_updated FROM analytics_summary')
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/api/v1/analytics/market-summary', methods=['GET'])
def get_market_summary():
    try:
        rows = get_data_from_db()
        summary_data = []

        # Explicit index mapping for robust compatibility
        for row in rows:
            summary_data.append({
                "location": row[0],
                "total_listings": row[1],
                "average_price_ngn": row[2],
                "last_updated": row[3]
            })
            
        return jsonify(summary_data), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Running locally on internal development port 5005
    app.run(host='127.0.0.1', port=5005, debug=False)

