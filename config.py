import os

# ===================================================================
# SHARED CONFIGURATION & ABSOLUTE PATH RESOLUTION
# ===================================================================

# Dynamically calculates the absolute root path of Lagos-Secure-Portal
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Relational Database Clusters (Guarantees path lock across sub-directories)
ACADEMIC_DB = os.path.join(BASE_DIR, "academic_records.db")
ZANNIE_DB = os.path.join(BASE_DIR, "zannie_sales.db")
LEADS_DB = os.path.join(BASE_DIR, "lagos_leads.db")

# Restructured Domain Pathways
SYLLABUS_DIR = os.path.join(BASE_DIR, "academic_syllabus")
STUDENT_REPORTS_DIR = os.path.join(BASE_DIR, "data", "student_reports")

# Centralized Webhook Dispatch Routing Matrix
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/mock_crypto_channel_token"
