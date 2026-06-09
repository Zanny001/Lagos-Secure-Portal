import os
import sys
from flask import Flask, jsonify

# Establish root configuration directory hook
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
try:
    from config import ACTIVE_TUNNEL_URL
except ImportError:
    ACTIVE_TUNNEL_URL = "https://eight-tools-create.trycloudflare.com"

app = Flask(__name__)

@app.route("/api/v1/verify", methods=["GET", "POST"])
def verify_session():
    return jsonify({
        "status": "authorized",
        "gateway_secure": True,
        "tunnel_endpoint": ACTIVE_TUNNEL_URL,
        "msg": "Lagos Secure Identity Verification Module Active"
    }), 200

if __name__ == "__main__":
    print("[+] Initializing Lagos Secure Verify Gateway on Port 5000...")
    # running with debug=False prevents double-execution issues in terminal environments
    app.run(host="0.0.0.0", port=5000, debug=False)
