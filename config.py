import os
import json
from google.oauth2.service_account import Credentials

# ===================================================================
# SHARED CONFIGURATION & ABSOLUTE PATH RESOLUTION
# ===================================================================

# Dynamically calculates the absolute root path of Lagos-Secure-Portal
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ===================================================================
# DATABASE CLUSTERS & REMOTE GATEWAYS
# ===================================================================

# Remote PostgreSQL Gateway Connection String (Production Engine)
DATABASE_URL = os.environ.get('DATABASE_URL')

# Relational Database Clusters (Guarantees path lock across sub-directories)
# Fallback to local absolute paths if remote environment variables are absent
ACADEMIC_DB = os.environ.get('ACADEMIC_DB_URL', os.path.join(BASE_DIR, "academic_records.db"))
ZANNIE_DB = os.environ.get('ZANNIE_DB_URL', os.path.join(BASE_DIR, "zannie_sales.db"))
LEADS_DB = os.environ.get('LEADS_DB_URL', os.path.join(BASE_DIR, "lagos_leads.db"))

# ===================================================================
# CLOUD AUTHENTICATION MATRIX (GOOGLE SECURE INJECTION)
# ===================================================================

def get_google_credentials():
    """
    Dynamically loads Google Cloud credentials from Vercel environment variables 
    or falls back to the absolute local sandbox file.
    """
    env_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    
    if env_creds:
        # Production Engine: parse the Vercel cloud variable into a dictionary
        creds_dict = json.loads(env_creds)
        return Credentials.from_service_account_info(creds_dict)
    else:
        # Local Sandbox: load the secure file using an absolute path lock
        creds_path = os.path.join(BASE_DIR, 'credentials.json')
        return Credentials.from_service_account_file(creds_path)

# Initialize global Google service credentials
# Import this into your blueprints via: `from config import google_credentials`
google_credentials = get_google_credentials()

# ===================================================================
# RESTRUCTURED DOMAIN PATHWAYS & ROUTING
# ===================================================================

SYLLABUS_DIR = os.path.join(BASE_DIR, "academic_syllabus")
STUDENT_REPORTS_DIR = os.path.join(BASE_DIR, "data", "student_reports")

# Centralized Webhook Dispatch Routing Matrix
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', "https://discord.com/api/webhooks/mock_crypto_channel_token")
