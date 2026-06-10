import sqlite3
import os
from flask import Flask, jsonify
from config import DATABASE_URL, ACADEMIC_DB, ZANNIE_DB

# Import Blueprints
from modules.academic import academic_bp
from modules.zannie import zannie_bp
from modules.harvester import harvester_bp
from modules.scholarships import scholarships_bp

app = Flask(__name__)

# Blueprints
app.register_blueprint(academic_bp)
app.register_blueprint(zannie_bp)
app.register_blueprint(harvester_bp)
app.register_blueprint(scholarships_bp)

# ===================================================================
# PRIMARY PHYSICS CURRICULUM ROUTE
# ===================================================================
@app.route('/', methods=['GET'])
def serve_physics_assessments():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>IGCSE Physics: Nuclear & Space Assessment</title>
        <style>
            body { font-family: sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 20px; }
            .container { max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 8px; }
            .question { margin-bottom: 20px; padding: 15px; background: #334155; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>IGCSE Nuclear & Space Physics Assessment</h1>
            <div class="question">1. Define isotope and explain why they share identical chemical properties.</div>
            <div class="question">2. Describe the composition, charge, and penetrating power of an alpha particle.</div>
            <div class="question">3. Calculate the remaining fraction of a sample with an 8-day half-life after 24 days.</div>
            <div class="question">4. Contrast nuclear fission and fusion with real-world examples.</div>
            <div class="question">5. Rank alpha, beta, and gamma radiation by ionizing ability.</div>
            </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
