import sqlite3
import math
import requests
import os
import io
import markdown
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, abort, send_file
from config import ACADEMIC_DB, DISCORD_WEBHOOK_URL
from fpdf import FPDF

academic_bp = Blueprint('academic', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYLLABUS_DIR = os.path.join(BASE_DIR, "academic_syllabus")
PHYSICS_ANSWER_KEY = {
    1: {"question": "What are the fundamental dimensions of Force?", "topic": "Dimensions & Units", "correct": "A", "options": {"A": "MLT⁻²", "B": "ML²T⁻²", "C": "MLT⁻¹", "D": "M²LT⁻²"}},
    2: {"question": "Which of the following is a pure scalar quantity?", "topic": "Mechanics Core", "correct": "C", "options": {"A": "Weight", "B": "Velocity", "C": "Mass", "D": "Acceleration"}},
    3: {"question": "A body moving in a circular path at a constant speed exhibits a:", "topic": "Circular Motion", "correct": "B", "options": {"A": "Constant velocity", "B": "Centripetal acceleration", "C": "Zero acceleration", "D": "Constant momentum"}},
    4: {"question": "Calculate the work done when a force of 10N moves an object through 5m in its own direction.", "topic": "Mechanics Core", "correct": "A", "options": {"A": "50 J", "B": "2 J", "C": "0.5 J", "D": "15 J"}},
    5: {"question": "What is the dimensional formula for Work Done?", "topic": "Dimensions & Units", "correct": "D", "options": {"A": "MLT⁻²", "B": "ML³T⁻²", "C": "MLT⁻¹", "D": "ML²T⁻²"}},
    6: {"question": "The rate of change of momentum is directly proportional to the applied force. This is Newton's:", "topic": "Mechanics Core", "correct": "B", "options": {"A": "1st Law", "B": "2nd Law", "C": "3rd Law", "D": "Law of Gravitation"}},
    7: {"question": "The force that tracks a satellite in stable orbit around the earth is called:", "topic": "Circular Motion", "correct": "C", "options": {"A": "Frictional force", "B": "Electrostatic force", "C": "Gravitational force", "D": "Centrifugal force"}},
    8: {"question": "An object drops freely from a height. Its kinetic energy reaches its maximum point at:", "topic": "Mechanics Core", "correct": "A", "options": {"A": "Just before hitting the ground", "B": "The precise halfway point", "C": "The starting release point", "D": "Varies unpredictably"}},
    9: {"question": "Which of the following physical quantities is completely dimensionless?", "topic": "Dimensions & Units", "correct": "B", "options": {"A": "Acceleration", "B": "Refractive Index", "C": "Density", "D": "Speed"}},
    10: {"question": "The angular velocity of a particle moving in a circle of radius 2m with a linear speed of 10m/s is:", "topic": "Circular Motion", "correct": "D", "options": {"A": "20 rad/s", "B": "0.2 rad/s", "C": "2 rad/s", "D": "5 rad/s"}}
}

# ==========================================
# UPGRADE: ZERO-COST LOCAL CURRICULUM BANK
# ==========================================
LOCAL_CURRICULUM_BANK = {
    "physics": {
        "igcse": """
### Theme 1: Motion, Forces and Energy
* **Question 1:** A car accelerates uniformly from rest to a velocity of $20\text{ m/s}$ in $5\text{ seconds}$. Calculate the acceleration and the total distance covered.
    * *Solution:* * Acceleration $a = \frac{v - u}{t} = \frac{20 - 0}{5} = 4\text{ m/s}^2$.
        * Distance $s = ut + \frac{1}{2}at^2 = 0 + \frac{1}{2}(4)(5^2) = 50\text{ meters}$.
* **Question 2:** State the law of conservation of momentum and describe what happens during an inelastic collision.
    * *Solution:* The total momentum before a collision equals the total momentum after the collision, provided no external forces act. In an inelastic collision, kinetic energy is not conserved, but total momentum remains conserved.
        """,
        "waec": """
### Section A: Mechanics
* **Question 1:** A projectile is launched with an initial velocity of $50\text{ m/s}$ at an angle of $30^\circ$ to the horizontal. Determine its time of flight and maximum height reached. ($g = 10\text{ m/s}^2$)
    * *Solution:* * Time of flight $T = \frac{2u\sin\theta}{g} = \frac{2(50)\sin(30^\circ)}{10} = 5\text{ s}$.
        * Maximum height $H = \frac{u^2\sin^2\theta}{2g} = \frac{50^2 \cdot (0.5)^2}{2(10)} = 31.25\text{ m}$.
        """
    }
}

class AcademicPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, "Zannie Academic Portal — STEM Instructional Resource", ln=True, align="R")
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def get_db_connection():
    db_target = str(ACADEMIC_DB)
    if db_target.startswith("postgresql://") or db_target.startswith("postgres://"):
        import psycopg2
        return psycopg2.connect(db_target), True
    else:
        if os.environ.get('VERCEL'):
            db_path = os.path.join('/tmp', os.path.basename(db_target))
        else:
            db_path = db_target
        return sqlite3.connect(db_path), False

def dispatch_report_card_webhook(student_name, score, percentage, remarks, topic_breakdown):
    breakdown_msg = ""
    for k, v in topic_breakdown.items():
        breakdown_msg += f"🔹 **{k}**: `{v['correct']}/{v['total']}` ({v['pct']}%)\n"
    payload = {
        "embeds": [{
            "title": "📊 NEW PERFORMANCE ASSESSMENT RECORD LOGGED",
            "color": 16181,
            "fields": [
                {"name": "Student Profile Identity", "value": f"**{student_name}**", "inline": True},
                {"name": "Aggregated Accuracy Target", "value": f"`{score}/10` ({percentage}%)", "inline": True},
                {"name": "Summary Evaluation Remarks", "value": f"*{remarks}*", "inline": False},
                {"name": "Structural Section Breakdown Metrics", "value": breakdown_msg, "inline": False}
            ]
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass

@academic_bp.route("/", methods=["GET", "POST"])
def academic_dashboard_index():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip().upper()
        score = 0
        topic_performance = {}

        for q_id, info in PHYSICS_ANSWER_KEY.items():
            topic = info["topic"]
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            topic_performance[topic]["total"] += 1

            user_choice = request.form.get(f"q_{q_id}", "").strip().upper()
            if user_choice == info["correct"]:
                score += 1
                topic_performance[topic]["correct"] += 1

        for t_name, tracking_obj in topic_performance.items():
            tracking_obj["pct"] = int((tracking_obj["correct"] / tracking_obj["total"]) * 100)

        percentage = int((score / len(PHYSICS_ANSWER_KEY)) * 100)
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        current_date_str = now.strftime("%Y-%m-%d")

        if percentage >= 85:
            remarks = "Excellent evaluation profile. Outstanding mastery observed across tracks."
        elif percentage >= 70:
            remarks = "Competent performance standard. Good retention stability across target core vectors."
        else:
            remarks = "Targeted instructional review sessions recommended to build consistency."

        try:
            conn, is_postgres = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO grades (student_name, subject, score, record_date) VALUES (%s, %s, %s, %s)" if is_postgres else "INSERT INTO grades (student_name, subject, score, record_date) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (student_name, "Physics", float(percentage), current_date_str))
            conn.commit()
            conn.close()
        except Exception:
            pass

        dispatch_report_card_webhook(student_name, score, percentage, remarks, topic_performance)
        report = {"name": student_name, "score": score, "pct": percentage, "remarks": remarks, "breakdown": topic_performance, "time": current_time_str}
        return render_template("academic.html", report=report)

    return render_template("academic.html", questions=PHYSICS_ANSWER_KEY, report=None)

@academic_bp.route('/syllabus')
def syllabus_index():
    tree = {}
    if os.path.exists(SYLLABUS_DIR):
        for subject in os.listdir(SYLLABUS_DIR):
            subject_path = os.path.join(SYLLABUS_DIR, subject)
            if os.path.isdir(subject_path) and not subject.startswith('.'):
                tree[subject] = {}
                for level in os.listdir(subject_path):
                    level_path = os.path.join(subject_path, level)
                    if os.path.isdir(level_path) and not level.startswith('.'):
                        files = [f for f in os.listdir(level_path) if f.endswith('.md')]
                        tree[subject][level] = files
    return render_template("syllabus_browser.html", tree=tree)

@academic_bp.route('/syllabus/view/<subject>/<level>/<filename>')
def view_syllabus_file(subject, level, filename):
    target_path = os.path.abspath(os.path.join(SYLLABUS_DIR, subject, level, filename))
    safe_base = os.path.abspath(SYLLABUS_DIR)
    if not target_path.startswith(safe_base) or not os.path.exists(target_path):
        abort(404, description="Requested academic asset out of scope or missing.")
    with open(target_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    return render_template("syllabus_viewer.html", content=html_content, title=filename.replace('_template.md', '').replace('_', ' ').title(), subject=subject, level=level, filename=filename)

@academic_bp.route('/syllabus/download/<subject>/<level>/<filename>')
def download_syllabus_pdf(subject, level, filename):
    target_path = os.path.abspath(os.path.join(SYLLABUS_DIR, subject, level, filename))
    safe_base = os.path.abspath(SYLLABUS_DIR)
    if not target_path.startswith(safe_base) or not os.path.exists(target_path):
        abort(404)
    with open(target_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    pdf = AcademicPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 41, 59)
    clean_title = filename.replace('_template.md', '').replace('_', ' ').title()
    pdf.cell(0, 12, clean_title, ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 6, f"TRACK: {subject.upper()} | LEVEL: {level.replace('_', ' ').upper()}", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            pdf.ln(4)
            continue
        if cleaned_line.startswith("###"):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(13, 148, 136)
            pdf.cell(0, 8, cleaned_line.replace("###", "").strip(), ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(51, 65, 85)
        elif cleaned_line.startswith("##"):
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(79, 70, 229)
            pdf.cell(0, 10, cleaned_line.replace("##", "").strip(), ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(51, 65, 85)
        else:
            text = cleaned_line.replace("**", "").replace("*", "").replace("`", "")
            pdf.multi_cell(0, 6, text)

    pdf_buffer = io.BytesIO()
    pdf_string = pdf.output(dest='S')
    if isinstance(pdf_string, str):
        pdf_buffer.write(pdf_string.encode('latin1'))
    else:
        pdf_buffer.write(pdf_string)
    pdf_buffer.seek(0)
    output_filename = filename.replace('.md', '.pdf')
    return send_file(pdf_buffer, as_attachment=True, download_name=output_filename, mimetype='application/pdf')

@academic_bp.route("/api/academic_data", methods=["GET"])
def get_academic_analytics():
    try:
        conn, is_postgres = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_name, subject, score FROM grades")
        rows = cursor.fetchall()
        conn.close()

        raw_map = {}
        for row in rows:
            student, subject, score = row
            if subject not in raw_map: raw_map[subject] = {}
            if student not in raw_map[subject]: raw_map[subject][student] = []
            raw_map[subject][student].append(score)
        track_resolver = {"TWIN A": "IGCSE Core", "TWIN B": "IGCSE Core", "DEMI": "WAEC Tracker", "FEMI": "Int Foundation Programme"}
        payload_response = {}
        for subject, students_dict in raw_map.items():
            payload_response[subject] = []
            for student_name, scores in students_dict.items():
                n = len(scores)
                mean_score = sum(scores) / n if n > 0 else 0.0
                variance = sum((x - mean_score) ** 2 for x in scores) / n if n > 0 else 0.0
                std_deviation = math.sqrt(variance)
                status = "Excel" if mean_score >= 75.0 else "Stable" if mean_score >= 55.0 else "Intervention"
                payload_response[subject].append({
                    "name": student_name, "track": track_resolver.get(student_name, "General Core Matrix"),
                    "assessments": n, "mean": round(mean_score, 1), "std_dev": round(std_deviation, 2), "status": status
                })
        return jsonify(payload_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@academic_bp.route("/api/scores/add", methods=["POST", "OPTIONS"])
def add_manual_grade_entry():
    if request.method == "OPTIONS": return "", 200
    try:
        data = request.get_json() or {}
        student = data.get("student", "").strip().upper()
        subject = data.get("subject")
        score = data.get("score")
        date = data.get("date")
        conn, is_postgres = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO grades (student_name, subject, score, record_date) VALUES (%s, %s, %s, %s)" if is_postgres else "INSERT INTO grades (student_name, subject, score, record_date) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (student, subject, float(score), date))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Grade metric logged seamlessly."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@academic_bp.route("/api/tasks/create", methods=["POST", "OPTIONS"])
def create_task_blueprint():
    if request.method == "OPTIONS": return "", 200
    try:
        data = request.get_json() or {}
        conn, is_postgres = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO tasks (title, track, subject, max_weight, deadline, content_markdown) VALUES (%s, %s, %s, %s, %s, %s)" if is_postgres else "INSERT INTO tasks (title, track, subject, max_weight, deadline, content_markdown) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (data.get("title"), data.get("track"), data.get("subject"), int(data.get("max_weight", 100)), data.get("deadline"), data.get("content_markdown")))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Task matrix deployed."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@academic_bp.route('/curriculum/<subject>/<level>', methods=['GET'])
def render_curriculum(subject, level):
    sub_key = subject.lower()
    lvl_key = level.lower()
    
    if sub_key in LOCAL_CURRICULUM_BANK and lvl_key in LOCAL_CURRICULUM_BANK[sub_key]:
        raw_markdown = LOCAL_CURRICULUM_BANK[sub_key][lvl_key]
    else:
        raw_markdown = f"### Asset Matrix Pending\nNo localized curriculum configuration exists yet for **{subject.upper()} ({level.upper()})**."

    html_content = markdown.markdown(raw_markdown, extensions=['fenced_code', 'tables'])
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script>
        <title>{subject.capitalize()} - {level.upper()}</title>
    </head>
    <body class="bg-slate-950 text-slate-300 p-10 font-sans leading-relaxed">
        <div class="max-w-4xl mx-auto bg-slate-900 p-10 rounded-2xl shadow-2xl border border-slate-800">
            <h1 class="text-3xl font-black text-indigo-400 border-b border-slate-700 pb-4 mb-8">Zannie Local Curriculum Engine: {subject.capitalize()} ({level.upper()})</h1>
            <div class="prose prose-invert prose-indigo max-w-none">
                {html_content}
            </div>
            <div class="mt-12 pt-6 border-t border-slate-800 text-xs text-slate-600 font-mono text-center">
                Served locally with zero network dependencies. Fully operational.
            </div>
        </div>
    </body>
    </html>
    """
