import re
import os

api_path = "/home/userland/Lagos-Secure-Portal/realestate_api.py"
html_path = "/home/userland/Lagos-Secure-Portal/dashboard_index.html"

# 1. Update the API Gateway
with open(api_path, "r", encoding="utf-8") as f:
    api_content = f.read()

download_endpoint = """
@app.route('/api/v1/dashboard/reports/<name>', methods=['GET'])
def download_report(name):
    try:
        from flask import send_from_directory, jsonify
        safe_name = name.replace(' ', '_')
        filename = f"Zannie_Report_{safe_name}.pdf"
        reports_dir = "/home/userland/Lagos-Secure-Portal/reports"
        
        if os.path.exists(os.path.join(reports_dir, filename)):
            return send_from_directory(reports_dir, filename, as_attachment=True)
        return jsonify({"status": "error", "message": "File not found. Please compile reports first."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
"""

if "/api/v1/dashboard/reports/" not in api_content:
    api_content = api_content.replace("if __name__ == '__main__':", f"{download_endpoint}\n\nif __name__ == '__main__':")
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(api_content)
    print("API successfully patched with PDF download route.")

# 2. Update the HTML/JS Dashboard UI
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Fixed syntax: using Python strings and HTML entities to prevent terminal encoding errors
old_td = '<td class="p-4 text-right"><span class="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded text-xs font-medium">${student.status}</span></td>'
new_td = '''<td class="p-4 text-right">
            <a href="/api/v1/dashboard/reports/${encodeURIComponent(student.name)}" class="bg-slate-800 hover:bg-purple-600 text-white px-3 py-1.5 rounded text-xs transition shadow border border-slate-700 hover:border-purple-500">
                &#128229; Download PDF
            </a>
          </td>'''

if "&#128229; Download PDF" not in html_content:
    html_content = html_content.replace(old_td, new_td)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard UI successfully updated with download interfaces.")
