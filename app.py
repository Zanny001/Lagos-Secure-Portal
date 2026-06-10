import os
from flask import Flask, jsonify

app = Flask(__name__)

# Force landing page to render the Physics Curriculum
@app.route('/', methods=['GET'])
def serve_curriculum():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>IGCSE Physics | Nuclear & Space</title>
        <style>
            body { background: #0f172a; color: #e2e8f0; font-family: sans-serif; padding: 20px; }
            .container { max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; }
            h1 { color: #8b5cf6; }
            .content { line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>IGCSE Nuclear & Space Physics</h1>
            <div class="content">
                <p><strong>Nuclear Physics:</strong> Atoms consist of a nucleus orbited by electrons. Isotopes share proton numbers but differ in nucleon numbers. Spontaneous decay emits α, β, or γ radiation.</p>
                <p><strong>Space Physics:</strong> The Big Bang theory is supported by Cosmic Microwave Background Radiation (CMBR) and galactic redshift. Stars evolve from nebulae into white dwarfs or supernovas.</p>
                <hr>
                <h3>Practice Questions</h3>
                <p>1. Define isotope.</p>
                <p>2. Describe alpha particle composition.</p>
                <p>3. Explain half-life calculations.</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
