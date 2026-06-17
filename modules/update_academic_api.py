import re

file_path = "/home/userland/Lagos-Secure-Portal/realestate_api.py"

with open(file_path, "r") as f:
    content = f.read()

academic_endpoint_code = """@app.route('/api/v1/dashboard/academic', methods=['GET'])
def get_academic_stats():
    try:
        import sqlite3
        import os
        db_path = "/home/userland/Lagos-Secure-Portal/academic_stats.db"
        
        if not os.path.exists(db_path):
            return jsonify({"status": "success", "data": []}), 200
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Fetching the active roster
        c.execute("SELECT name, gender, program_track FROM students")
        rows = c.fetchall()
        conn.close()
        
        students_list = []
        for row in rows:
            students_list.append({
                "name": row[0],
                "gender": row[1],
                "program": row[2],
                "status": "Enrolled"
            })
            
        return jsonify({"status": "success", "data": students_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

# Append the route if it doesn't exist, or replace it if it does
if "@app.route('/api/v1/dashboard/academic'" in content:
    content = re.sub(r"@app\.route\('/api/v1/dashboard/academic'.*?500", academic_endpoint_code, content, flags=re.DOTALL)
else:
    # Find a clean spot right before the main entrypoint execution block
    content = content.replace("if __name__ == '__main__':", f"{academic_endpoint_code}\n\nif __name__ == '__main__':")

with open(file_path, "w") as f:
    f.write(content)

print("Core API successfully synced with the Path G Academic matrix.")
