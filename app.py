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

# ===================================================================
# DYNAMIC DATABASE RESOLUTION (SQLITE / POSTGRES HYBRID ENGINE)
# ===================================================================
def execute_init_query(db_target, sqlite_query, postgres_query):
    """Executes schema initialization depending on the targeted database connection dialect."""
    try:
        if str(db_target).startswith("postgresql://") or str(db_target).startswith("postgres://"):
            import psycopg2
            conn = psycopg2.connect(db_target)
            cursor = conn.cursor()
            cursor.execute(postgres_query)
            conn.commit()
            conn.close()
        else:
            if os.environ.get('VERCEL'):
                db_path = os.path.join('/tmp', os.path.basename(db_target))
            else:
                db_path = db_target

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sqlite_query)
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"[-] Database initialization warning for target {db_target}: {str(e)}")

# ===================================================================
# DATABASE INITIALIZATION ROUTINES
# ===================================================================
def init_all_databases():
    """Initializes schema dependencies across SQLite or PostgreSQL clusters."""

    # Academic Tables
    execute_init_query(
        ACADEMIC_DB,
        "CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT NOT NULL, subject TEXT NOT NULL, score REAL NOT NULL, record_date TEXT NOT NULL);",
        "CREATE TABLE IF NOT EXISTS grades (id SERIAL PRIMARY KEY, student_name TEXT NOT NULL, subject TEXT NOT NULL, score REAL NOT NULL, record_date TIMESTAMPTZ NOT NULL);"
    )

    execute_init_query(
        ACADEMIC_DB,
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, track TEXT NOT NULL, subject TEXT NOT NULL, max_weight INTEGER NOT NULL, deadline TEXT, content_markdown TEXT NOT NULL);",
        "CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT NOT NULL, track TEXT NOT NULL, subject TEXT NOT NULL, max_weight INTEGER NOT NULL, deadline TIMESTAMPTZ, content_markdown TEXT NOT NULL);"
    )

    # Zannie Core E-commerce Tables
    execute_init_query(
        ZANNIE_DB,
        "CREATE TABLE IF NOT EXISTS custom_orders (order_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, customer_email TEXT NOT NULL, customer_phone TEXT, garment_name TEXT NOT NULL, base_price_ngn REAL NOT NULL, order_status TEXT DEFAULT 'Pending' CHECK(order_status IN ('Pending', 'Processing', 'Dispatched', 'Completed', 'Cancelled')), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "CREATE TABLE IF NOT EXISTS custom_orders (order_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, customer_email TEXT NOT NULL, customer_phone TEXT, garment_name TEXT NOT NULL, base_price_ngn REAL NOT NULL, order_status TEXT DEFAULT 'Pending' CHECK(order_status IN ('Pending', 'Processing', 'Dispatched', 'Completed', 'Cancelled')), created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);"
    )

    execute_init_query(
        ZANNIE_DB,
        "CREATE TABLE IF NOT EXISTS order_specifications (spec_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, fabric_matrix TEXT, embroidery_profile TEXT, measurements_json TEXT, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id) ON DELETE CASCADE);",
        "CREATE TABLE IF NOT EXISTS order_specifications (spec_id SERIAL PRIMARY KEY, order_id TEXT NOT NULL, fabric_matrix TEXT, embroidery_profile TEXT, measurements_json TEXT, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id) ON DELETE CASCADE);"
    )

    execute_init_query(
        ZANNIE_DB,
        "CREATE TABLE IF NOT EXISTS transaction_logs (transaction_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, gateway TEXT NOT NULL CHECK(gateway IN ('Paystack', 'Flutterwave')), currency_code TEXT NOT NULL CHECK(currency_code IN ('NGN', 'USD', 'GBP', 'EUR')), amount_paid REAL NOT NULL, gateway_reference TEXT UNIQUE, payment_status TEXT NOT NULL CHECK(payment_status IN ('Initiated', 'Successful', 'Failed', 'Reversed')), updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id));",
        "CREATE TABLE IF NOT EXISTS transaction_logs (transaction_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, gateway TEXT NOT NULL CHECK(gateway IN ('Paystack', 'Flutterwave')), currency_code TEXT NOT NULL CHECK(currency_code IN ('NGN', 'USD', 'GBP', 'EUR')), amount_paid REAL NOT NULL, gateway_reference TEXT UNIQUE, payment_status TEXT NOT NULL CHECK(payment_status IN ('Initiated', 'Successful', 'Failed', 'Reversed')), updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (order_id) REFERENCES custom_orders(order_id));"
    )

    print("[+] Unified operational database clusters synchronized successfully.")

init_all_databases()

# ===================================================================
# BLUEPRINT REGISTRATION
# ===================================================================
app.register_blueprint(academic_bp)
app.register_blueprint(zannie_bp)
app.register_blueprint(harvester_bp)
app.register_blueprint(scholarships_bp)

# ===================================================================
# PRIMARY ROOT ROUTE: EXTENDED CURRICULUM VIEW
# ===================================================================
@app.route('/', methods=['GET'])
def serve_physics_assessments():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Academic Center | IGCSE Physics</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
            .container { max-width: 850px; margin: 0 auto; background: #1e293b; padding: 35px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
            h1 { color: #8b5cf6; border-bottom: 2px solid #334155; padding-bottom: 10px; }
            .note-section { background: #334155; padding: 20px; border-left: 4px solid #38bdf8; border-radius: 6px; margin: 20px 0; }
            .question-card { background: #0f172a; padding: 15px; margin: 10px 0; border-radius: 6px; border: 1px solid #334155; }
            .num { color: #fbbf24; font-weight: bold; margin-right: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>IGCSE Extended Curriculum: Nuclear & Space Physics</h1>
            
            <div class="note-section">
                <h3>Lesson Summary</h3>
                <p><strong>Nuclear Physics:</strong> Nuclei consist of protons and neutrons. Isotopes share proton numbers but vary in neutrons. Unstable configurations decay via alpha, beta, or gamma emissions.</p>
                <p><strong>Space Physics:</strong> Stellar progression spans from stellar nebulae to white dwarfs or supernovas depending on starting mass. Cosmic expansion models are fundamentally mapped through redshift observations.</p>
            </div>

            <h3>20 Practice Questions Portfolio</h3>
            <div class="question-card"><span class="num">Q1.</span> Define the term isotope and explain why isotopes of the same element have identical chemical properties.</div>
            <div class="question-card"><span class="num">Q2.</span> Describe the composition, charge, and relative penetrating power of an alpha particle.</div>
            <div class="question-card"><span class="num">Q3.</span> A radioactive sample has a half-life of 8 days. Calculate the fraction of the original sample remaining after 24 days.</div>
            <div class="question-card"><span class="num">Q4.</span> Explain the difference between nuclear fission and nuclear fusion, providing an example of where each occurs.</div>
            <div class="question-card"><span class="num">Q5.</span> Compare the ionizing abilities of alpha, beta, and gamma radiation, and explain why gamma is the least ionizing.</div>
            <div class="question-card"><span class="num">Q6.</span> Describe Rutherford's alpha-particle scattering experiment and explain how it led to the nuclear model of the atom.</div>
            <div class="question-card"><span class="num">Q7.</span> Write the balanced nuclear equation for the beta decay of Carbon-14.</div>
            <div class="question-card"><span class="num">Q8.</span> Define background radiation and state two natural and two artificial sources.</div>
            <div class="question-card"><span class="num">Q9.</span> State Hubble's Law and explain how it provides evidence for the expansion of the universe.</div>
            <div class="question-card"><span class="num">Q10.</span> Describe the significance of the Cosmic Microwave Background Radiation (CMBR) in modern cosmology.</div>
            <div class="question-card"><span class="num">Q11.</span> Outline the life cycle of a star with a mass similar to our Sun, from nebula to white dwarf.</div>
            <div class="question-card"><span class="num">Q12.</span> What is a supernova? Explain which type of stars undergo this process.</div>
            <div class="question-card"><span class="num">Q13.</span> Explain how the redshift of light from distant galaxies is measured and what it indicates about their relative velocity.</div>
            <div class="question-card"><span class="num">Q14.</span> Describe the relationship between a planet's orbital speed and its distance from the star it orbits.</div>
            <div class="question-card"><span class="num">Q15.</span> Define a light-year and explain why it is a necessary unit of measurement in space physics.</div>
            <div class="question-card"><span class="num">Q16.</span> Compare the final evolutionary stages of a high-mass star (neutron star vs. black hole).</div>
            <div class="question-card"><span class="num">Q17.</span> State the safety precautions that must be taken when handling, storing, and disposing of radioactive materials.</div>
            <div class="question-card"><span class="num">Q18.</span> Explain the process of hydrogen fusion in a stable star and how it maintains the star's equilibrium against gravitational collapse.</div>
            <div class="question-card"><span class="num">Q19.</span> Describe how to calculate the recessional velocity of a galaxy if its redshift and the Hubble constant are known.</div>
            <div class="question-card"><span class="num">Q20.</span> Discuss the environmental advantages and disadvantages of using nuclear power compared to fossil fuels.</div>
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
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/v1/health", methods=["GET"])
def global_system_health():
    is_postgres = str(ACADEMIC_DB).startswith("postgres")
    return jsonify({
        "status": "online",
        "environment": "Unified Production Matrix (Cloud)" if os.environ.get('VERCEL') else "Local Staging Matrix (UserLAnd)",
        "database_layer": "Remote PostgreSQL Cluster" if is_postgres else "Local Ephemeral Storage",
        "modules_active": [
            "Academic Analytics Engine v2",
            "Zannie Multi-Currency Checkout",
            "Harvester Intelligence",
            "Global Scholarships Matrix"
        ]
    }), 200

@app.route('/favicon.ico')
def favicon():
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
