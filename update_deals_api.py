import re

file_path = "/home/userland/Lagos-Secure-Portal/realestate_api.py"

with open(file_path, "r") as f:
    content = f.read()

deals_endpoint_code = """@app.route('/api/v1/dashboard/deals', methods=['GET'])
def get_harvested_deals():
    try:
        import sqlite3
        db_path = "/home/userland/Lagos-Secure-Portal/deal_harvester.db"
        
        if not os.path.exists(db_path):
            return jsonify({"status": "success", "data": []}), 200
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT device_name, original_price, discount_price, savings_percent, affiliate_link FROM active_deals")
        rows = c.fetchall()
        conn.close()
        
        deals_list = []
        for row in rows:
            deals_list.append({
                "device": row[0],
                "original": row[1],
                "discount": row[2],
                "savings": row[3],
                "link": row[4]
            })
            
        return jsonify({"status": "success", "data": deals_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

# Append the route if it doesn't exist, or replace it if it does
if "@app.route('/api/v1/dashboard/deals'" in content:
    content = re.sub(r"@app\.route\('/api/v1/dashboard/deals'.*?500", deals_endpoint_code, content, flags=re.DOTALL)
else:
    # Find a clean spot right before the main entrypoint execution block
    content = content.replace("if __name__ == '__main__':", f"{deals_endpoint_code}\n\nif __name__ == '__main__':")

with open(file_path, "w") as f:
    f.write(content)

print("Core API successfully synced with multi-store affiliate schema.")
