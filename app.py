import os
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Global variable required by Vercel's Python runtime
app = Flask(__name__)

# Mock Discord Webhook for syncing system metrics
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/mock_crypto_channel_token"

# Curricular Question Bank Architecture
PHYSICS_ANSWER_KEY = {
    1: {"question": "What are the fundamental dimensions of Force?", "topic": "Dimensions", "correct": "A", "options": {"A": "MLT⁻²", "B": "ML²T⁻²", "C": "MLT⁻¹", "D": "M²LT⁻²"}},
    2: {"question": "Which of the following is a scalar quantity?", "topic": "Mechanics", "correct": "C", "options": {"A": "Weight", "B": "Velocity", "C": "Mass", "D": "Acceleration"}},
    3: {"question": "A body moving in a circular path at a constant speed has a:", "topic": "Circular Motion", "correct": "B", "options": {"A": "Constant velocity", "B": "Centripetal acceleration", "C": "Zero acceleration", "D": "Constant momentum"}},
    4: {"question": "Calculate the work done when a force of 10N moves an object through 5m in its own direction.", "topic": "Mechanics", "correct": "A", "options": {"A": "50 J", "B": "2 J", "C": "0.5 J", "D": "15 J"}},
    5: {"question": "What is the dimensional formula for Work Done?", "topic": "Dimensions", "correct": "D", "options": {"A": "MLT⁻²", "B": "ML³T⁻²", "C": "MLT⁻¹", "D": "ML²T⁻²"}},
    6: {"question": "The rate of change of momentum is directly proportional to the applied force. This is Newton's:", "topic": "Mechanics", "correct": "B", "options": {"A": "1st Law", "B": "2nd Law", "C": "3rd Law", "D": "Law of Gravitation"}},
    7: {"question": "The force that keeps a satellite in orbit around the earth is called:", "topic": "Circular Motion", "correct": "C", "options": {"A": "Frictional force", "B": "Electrostatic force", "C": "Gravitational force", "D": "Centrifugal force"}},
    8: {"question": "An object drops from a height. Its kinetic energy is maximum at:", "topic": "Mechanics", "correct": "A", "options": {"A": "Just before hitting the ground", "B": "The halfway point", "C": "The starting point", "D": "Varies unpredictably"}},
    9: {"question": "Which of the following quantities is dimensionless?", "topic": "Dimensions", "correct": "B", "options": {"A": "Acceleration", "B": "Refractive Index", "C": "Density", "D": "Speed"}},
    10: {"question": "The angular velocity of a particle moving in a circle of radius 2m with a linear speed of 10m/s is:", "topic": "Circular Motion", "correct": "D", "options": {"A": "20 rad/s", "B": "0.2 rad/s", "C": "2 rad/s", "D": "5 rad/s"}}
}

# Production Visual Dashboard HTML UI Core
VISUAL_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lagos Secure Portal — Analytics</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen font-sans antialiased">
    <div class="max-w-4xl mx-auto p-4 md:p-8">
        
        <header class="border-b border-teal-500/30 pb-6 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
                    Lagos Secure Portal — Academic Engine
                </h1>
                <p class="text-sm text-slate-400 mt-1">Real-time curriculum assessment, student metrics charting, and reporting pipeline.</p>
            </div>
            <div class="text-xs bg-slate-800 border border-slate-700 px-3 py-2 rounded-md font-mono text-slate-400">
                Environment: Vercel Production
            </div>
        </header>

        {% if report %}
        <main class="space-y-6">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                <div class="flex flex-wrap justify-between items-center gap-4 border-b border-slate-700/60 pb-4 mb-6">
                    <div>
                        <span class="text-xs font-semibold uppercase tracking-wider text-teal-400">Target Candidate Evaluation Card</span>
                        <h2 class="text-2xl font-bold text-white mt-0.5">👤 {{ report.name }}</h2>
                    </div>
                    <div class="text-right">
                        <span class="text-xs text-slate-400 block">Assessment New Timestamp</span>
                        <span class="text-sm font-mono font-medium text-slate-200">{{ report.time }}</span>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div class="bg-slate-990 bg-slate-900/60 border border-slate-700/50 p-4 rounded-lg">
                        <span class="text-xs font-medium text-slate-400 uppercase">Raw Score Metric</span>
                        <div class="text-3xl font-black text-white mt-1">{{ report.score }} <span class="text-lg font-normal text-slate-500">/ 10</span></div>
                    </div>
                    <div class="bg-slate-900/60 border border-slate-700/50 p-4 rounded-lg">
                        <span class="text-xs font-medium text-slate-400 uppercase">Percentage Accuracy</span>
                        <div class="text-3xl font-black text-teal-400 mt-1">{{ report.pct }}%</div>
                    </div>
                    <div class="bg-slate-900/60 border border-slate-700/50 p-4 rounded-lg">
                        <span class="text-xs font-medium text-slate-400 uppercase">Verification Routing</span>
                        <div class="text-sm font-semibold text-emerald-400 mt-2.5 flex items-center gap-1.5">
                            <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span> Synchronized to Channel
                        </div>
                    </div>
                </div>

                <div class="bg-slate-900/40 border border-teal-500/20 px-4 py-3 rounded-lg text-sm text-slate-300 italic mb-6">
                    "{{ report.remarks }}"
                </div>

                <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">📊 Structural Curricular Domain Mastery Curves</h3>
                <div class="space-y-4 bg-slate-900/30 p-4 rounded-lg border border-slate-700/40">
                    {% for topic, stats in report.breakdown.items() %}
                    <div>
                        <div class="flex justify-between text-xs font-semibold mb-1">
                            <span class="text-slate-300">{{ topic }}</span>
                            <span class="text-slate-400">{{ stats.correct }} / {{ stats.total }} Correct ({{ stats.pct }}%)</span>
                        </div>
                        <div class="w-full bg-slate-700 h-2.5 rounded-full overflow-hidden">
                            {% if stats.pct >= 80 %}
                                <div class="bg-emerald-400 h-full rounded-full" style="width: {{ stats.pct ~ '%' }}"></div>
                            {% elif stats.pct >= 50 %}
                                <div class="bg-amber-400 h-full rounded-full" style="width: {{ stats.pct ~ '%' }}"></div>
                            {% else %}
                                <div class="bg-rose-500 h-full rounded-full" style="width: {{ stats.pct ~ '%' }}"></div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <div class="mt-8 pt-4 border-t border-slate-700/60 text-center">
                    <a href="/" class="inline-flex items-center gap-2 text-sm font-bold text-teal-400 hover:text-teal-300 transition-colors">
                        ← Launch Fresh Performance Assessment Session
                    </a>
                </div>
            </div>
        </main>
        {% else %}
        <main>
            <form method="POST" class="space-y-6">
                <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                    <label class="block text-sm font-bold tracking-wide uppercase text-teal-400 mb-2" for="student_name">
                        Student Full Identity Name Reference:
                    </label>
                    <input type="text" id="student_name" name="student_name" required placeholder="e.g., TOOKI" 
                           class="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-colors font-medium">
                </div>

                <div class="space-y-4">
                    {% for q_id, info in questions.items() %}
                    <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="px-2 py-0.5 bg-slate-900 border border-slate-700 rounded text-[11px] font-bold tracking-wider uppercase text-slate-400">
                                {{ info.topic }}
                            </span>
                            <span class="text-xs font-mono text-slate-500 font-semibold">Item #{{ q_id }}</span>
                        </div>
                        <p class="text-white font-medium text-base leading-relaxed">
                            {{ info.question }}
                        </p>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-1">
                            {% for letter, option_text in info.options.items() %}
                            <label class="flex items-center gap-3 bg-slate-900/50 border border-slate-700/60 rounded-lg p-3 hover:bg-slate-700/40 hover:border-slate-600 transition-all cursor-pointer">
                                <input type="radio" name="q_{{ q_id }}" value="{{ letter }}" required
                                       class="h-4 w-4 accent-teal-500 text-teal-600 bg-slate-900 border-slate-700 focus:ring-offset-slate-900">
                                <span class="text-sm text-slate-300"><b class="text-teal-400 font-bold font-mono mr-1">{{ letter }})</b> {{ option_text }}</span>
                            </label>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <button type="submit" class="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-bold py-3.5 px-6 rounded-xl shadow-lg shadow-teal-500/10 transition-all text-center tracking-wide text-base">
                    Compile Data Parameters & Sync Metrics
                </button>
            </form>
        </main>
        {% endif %}
    </div>
</body>
</html>
"""

def dispatch_report_card_webhook(student_name, score, percentage, remarks, topic_breakdown):
    """Transmits report metrics payload summaries directly to active Discord channels."""
    breakdown_msg = ""
    for k, v in topic_breakdown.items():
        breakdown_msg += f"🔹 **{k}**: `{v['correct']}/{v['total']}` ({v['pct']}%)\n"

    payload = {
        "embeds": [{
            "title": "📊 VERCEL PRODUCTION ASSESSMENT GENERATOR STATUS",
            "color": 16181,
            "fields": [
                {"name": "Student Profile Identity", "value": f"**{student_name}**", "inline": True},
                {"name": "Aggregated Accuracy Target", "value": f"`{score}/10` ({percentage}%)", "inline": True},
                {"name": "Summary Evaluation Remarks", "value": f"*{remarks}*", "inline": False},
                {"name": "Structural Section Breakdown Metrics", "value": breakdown_msg, "inline": False}
            ],
            "footer": {"text": "Vercel Cloud Production Router Asset Instance"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"[DISCORD DISPATCH FAULT] Logging bypass error trace: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip().upper()
        score = 0
        topic_performance = {}

        # Parse metrics arrays against key models
        for q_id, info in PHYSICS_ANSWER_KEY.items():
            topic = info["topic"]
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            topic_performance[topic]["total"] += 1

            user_choice = request.form.get(f"q_{q_id}", "").strip().upper()
            if user_choice == info["correct"]:
                score += 1
                topic_performance[topic]["correct"] += 1

        # Post-process percentages across topic subcategories
        for t_name, tracking_obj in topic_performance.items():
            tracking_obj["pct"] = int((tracking_obj["correct"] / tracking_obj["total"]) * 100)

        percentage = int((score / len(PHYSICS_ANSWER_KEY)) * 100)
        
        if percentage >= 85:
            remarks = "Excellent evaluation profile. Outstanding data-point mastery observed across execution tracks."
        elif percentage >= 70:
            remarks = "Competent performance standard. Good retention stability across target core vectors."
        else:
            remarks = "Targeted instructional review sessions recommended to build consistency in weak domains."

        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Trigger outbound reporting updates
        dispatch_report_card_webhook(student_name, score, percentage, remarks, topic_performance)

        report = {
            "name": student_name, "score": score, "pct": percentage, 
            "remarks": remarks, "breakdown": topic_performance, "time": current_time_str
        }
        return render_template_string(VISUAL_DASHBOARD_TEMPLATE, report=report)

    # Render form tracking panel immediately on GET request
    return render_template_string(VISUAL_DASHBOARD_TEMPLATE, questions=PHYSICS_ANSWER_KEY, report=None)

# Added backward compatibility verification route layer
@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "service": "Lagos Secure Verify Engine",
        "environment": "Vercel Serverless"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
