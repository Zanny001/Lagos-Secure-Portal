import re

file_path = "/home/userland/Lagos-Secure-Portal/realestate_api.py"

with open(file_path, "r") as f:
    content = f.read()

compiler_endpoint = """
@app.route('/api/v1/dashboard/compile_reports', methods=['POST'])
def trigger_compiler():
    try:
        import subprocess
        # Execute the ReportLab engine
        process = subprocess.run(['python3', '/home/userland/Lagos-Secure-Portal/modules/generate_reports.py'], capture_output=True, text=True)
        
        if process.returncode == 0:
            return jsonify({"status": "success", "message": "All PDF reports successfully compiled to the /reports directory."}), 200
        else:
            return jsonify({"status": "error", "message": f"Compilation failed: {process.stderr}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
"""

if "/api/v1/dashboard/compile_reports" not in content:
    content = content.replace("if __name__ == '__main__':", f"{compiler_endpoint}\n\nif __name__ == '__main__':")
    
    with open(file_path, "w") as f:
        f.write(content)
    print("API patched with the PDF compiler endpoint.")
else:
    print("Compiler endpoint already exists.")
