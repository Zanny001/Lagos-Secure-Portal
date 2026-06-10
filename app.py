import sqlite3
import os
from flask import Flask, jsonify, request
from config import DATABASE_URL, ACADEMIC_DB, ZANNIE_DB

# Import Blueprints
from modules.academic import academic_bp
from modules.zannie import zannie_bp
from modules.harvester import harvester_bp
from modules.scholarships import scholarships_bp

app = Flask(__name__)

# ===================================================================
# DYNAMIC DATABASE RESOLUTION
# ===================================================================
def execute_init_query(db_target, sqlite_query, postgres_query):
    try:
        if str(db_target).startswith("postgresql://") or str(db_target).startswith("postgres://"):
            import psycopg2
            conn = psycopg2.connect(db_target)
            cursor = conn.cursor()
            cursor.execute(postgres_query)
            conn.commit()
            conn.close()
        else:
            db_path = os.path.join('/tmp', os.path.basename(db_target)) if os.environ.get('VERCEL') else db_target
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sqlite_query)
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"[-] Database initialization warning for target {db_target}: {str(e)}")

def init_all_databases():
    execute_init_query(
        ACADEMIC_DB,
        "CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT NOT NULL, subject TEXT NOT NULL, score REAL NOT NULL, record_date TEXT NOT NULL);",
        "CREATE TABLE IF NOT EXISTS grades (id SERIAL PRIMARY KEY, student_name TEXT NOT NULL, subject TEXT NOT NULL, score REAL NOT NULL, record_date TIMESTAMPTZ NOT NULL);"
    )
init_all_databases()

# ===================================================================
# BLUEPRINT REGISTRATION
# ===================================================================
app.register_blueprint(academic_bp)
app.register_blueprint(zannie_bp)
app.register_blueprint(harvester_bp)
app.register_blueprint(scholarships_bp)

# ===================================================================
# PRIMARY CURRICULUM OVERRIDE ROUTE
# ===================================================================
@app.route('/', methods=['GET'])
def serve_physics_assessments():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Academic Center | IGCSE Physics Assessments</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; line-height: 1.6; }
            .container { max-width: 900px; margin: 0 auto; background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
            h1 { color: #8b5cf6; border-bottom: 2px solid #334155; padding-bottom: 10px; font-size: 28px; }
            h2 { color: #38bdf8; margin-top: 35px; font-size: 22px; }
            .note-box { background: #334155; padding: 25px; border-left: 5px solid #8b5cf6; border-radius: 8px; margin-bottom: 30px; }
            .question { background: #0f172a; padding: 18px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #334155; font-size: 16px; }
            .question-num { color: #fbbf24; font-weight: bold; margin-right: 10px; font-size: 18px; }
            strong { color: #f8fafc; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>IGCSE Extended Curriculum: Nuclear & Space Physics</h1>
            
            <div class="note-box">
                <h2>Lesson Notes Summary</h2>
                <p><strong>1. Nuclear Physics:</strong> Atoms consist of a central nucleus (protons and neutrons) orbited by electrons. Isotopes have the same proton number but different nucleon numbers. Unstable nuclei undergo spontaneous radioactive decay, emitting α (helium nuclei), β (high-energy electrons), or γ (electromagnetic waves) radiation. Half-life is the time taken for half the radioactive nuclei in a sample to decay. Fission involves splitting a heavy nucleus, while fusion involves combining light nuclei.</p>
                <p><strong>2. Space Physics:</strong> The universe originated from the Big Bang, supported by CMBR (Cosmic Microwave Background Radiation) and the redshift of light from distant galaxies (Hubble's Law). Stars form from nebulae, fusing hydrogen into helium. Average stars become white dwarfs, while massive stars undergo supernova explosions, leaving behind neutron stars or black holes.</p>
            </div>

            <h2>20 Practice Questions</h2>
            <div class="question"><span class="question-num">Q1.</span> Define the term isotope and explain why isotopes of the same element have identical chemical properties.</div>
            <div class="question"><span class="question-num">Q2.</span> Describe the composition, charge, and relative penetrating power of an alpha particle.</div>
            <div class="question"><span class="question-num">Q3.</span> A radioactive sample has a half-life of 8 days. Calculate the fraction of the original sample remaining after 24 days.</div>
            <div class="question"><span class="question-num">Q4.</span> Explain the difference between nuclear fission and nuclear fusion, providing an example of where each occurs.</div>
            <div class="question"><span class="question-num">Q5.</span> Compare the ionizing abilities of alpha, beta, and gamma radiation, and explain why gamma is the least ionizing.</div>
            <div class="question"><span class="question-num">Q6.</span> Describe Rutherford's alpha-particle scattering experiment and explain how it led to the nuclear model of the atom.</div>
            <div class="question"><span class="question-num">Q7.</span> Write the balanced nuclear equation for the beta decay of Carbon-14.</div>
            <div class="question"><span class="question-num">Q8.</span> Define background radiation and state two natural and two artificial sources.</div>
            <div class="question"><span class="question-num">Q9.</span> State Hubble's Law and explain how it provides evidence for the expansion of the universe.</div>
            <div class="question"><span class="question-num">Q10.</span> Describe the significance of the Cosmic Microwave Background Radiation (CMBR) in modern cosmology.</div>
            <div class="question"><span class="question-num">Q11.</span> Outline the life cycle of a star with a mass similar to our Sun, from nebula to white dwarf.</div>
            <div class="question"><span class="question-num">Q12.</span> What is a supernova? Explain which type of stars undergo this process.</div>
            <div class="question"><span class="question-num">Q13.</span> Explain how the redshift of light from distant galaxies is measured and what it indicates about their relative velocity.</div>
            <div class="question"><span class="question-num">Q14.</span> Describe the relationship between a planet's orbital speed and its distance from the star it orbits.</div>
            <div class="question"><span class="question-num">Q15.</span> Define a light-year and explain why it is a necessary unit of measurement in space physics.</div>
            <div class="question"><span class="question-num">Q16.</span> Compare the final evolutionary stages of a high-mass star (neutron star vs. black hole).</div>
            <div class="question"><span class="question-num">Q17.</span> State the safety precautions that must be taken when handling, storing, and disposing of radioactive materials.</div>
            <div class="question"><span class="question-num">Q18.</span> Explain the process of hydrogen fusion in a stable star and how it maintains the star's equilibrium against gravitational collapse.</div>
            <div class="question"><span class="question-num">Q19.</span> Describe how to calculate the recessional velocity of a galaxy if its redshift and the Hubble constant are known.</div>
            <div class="question"><span class="question-num">Q20.</span> Discuss the environmental advantages and disadvantages of using nuclear power compared to fossil fuels.</div>
        </div>
    </body>
    </html>
    """

# ===================================================================
# SYSTEM GLOBAL HEALTH CHECK & MIDDLEWARE
# ===================================================================
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/api/v1/health", methods=["GET"])
def global_system_health():
    return jsonify({ "status": "online", "environment": "Vercel Production Matrix" }), 200                                                                                                                                                 

if __name__ == "__main__":                                                    
    app.run(host="0.0.0.0", port=5001, debug=True)
