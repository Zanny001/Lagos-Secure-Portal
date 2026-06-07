import sqlite3
import math
import requests
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from config import ACADEMIC_DB, DISCORD_WEBHOOK_URL

# ===================================================================
# MODULE A: ACADEMIC BLUEPRINT
# ===================================================================
academic_bp = Blueprint('academic', __name__)

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
            remarks = "Excellent evaluation profile. Outstanding data-point mastery observed across execution tracks."
        elif percentage >= 70:
            remarks = "Competent performance standard. Good retention stability across target core vectors."
        else:
            remarks = "Targeted instructional review sessions recommended to build consistency in weak domains."

        try:
            conn = sqlite3.connect(ACADEMIC_DB)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO grades (student_name, subject, score, record_date) VALUES (?, ?, ?, ?)",
                (student_name, "Physics", float(percentage), current_date_str)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

        dispatch_report_card_webhook(student_name, score, percentage, remarks, topic_performance)

        report = {
            "name": student_name, "score": score, "pct": percentage,
            "remarks": remarks, "breakdown": topic_performance, "time": current_time_str
        }
        return render_template("academic.html", report=report)

    return render_template("academic.html", questions=PHYSICS_ANSWER_KEY, report=None)

@academic_bp.route("/api/academic_data", methods=["GET"])
def get_academic_analytics():
    try:
        conn = sqlite3.connect(ACADEMIC_DB)
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
            
        track_resolver = {
            "TWIN A": "IGCSE Core", 
            "TWIN B": "IGCSE Core", 
            "DEMI": "WAEC Tracker",
            "FEMI": "Int Foundation Programme"
        }
        
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
                    "name": student_name,
                    "track": track_resolver.get(student_name, "General Core Matrix"),
                    "assessments": n,
                    "mean": round(mean_score, 1),
                    "std_dev": round(std_deviation, 2),
                    "status": status
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

        conn = sqlite3.connect(ACADEMIC_DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO grades (student_name, subject, score, record_date) VALUES (?, ?, ?, ?)", (student, subject, float(score), date))
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
        conn = sqlite3.connect(ACADEMIC_DB)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, track, subject, max_weight, deadline, content_markdown) VALUES (?, ?, ?, ?, ?, ?)",
            (data.get("title"), data.get("track"), data.get("subject"), int(data.get("max_weight", 100)), data.get("deadline"), data.get("content_markdown"))
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Task matrix deployed."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
