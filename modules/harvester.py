import os
import sqlite3
import re
import requests
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect
import psycopg2
from config import LEADS_DB

harvester_bp = Blueprint('harvester', __name__)

# --- Webhook Configuration ---
# Two-tier architecture for public leads and private premium execution
PUBLIC_WEBHOOK_URL = os.environ.get("PUBLIC_WEBHOOK_URL", "")
PRIVATE_WEBHOOK_URL = os.environ.get("PRIVATE_WEBHOOK_URL", "")

def get_db_connection():
    if str(LEADS_DB).startswith("postgresql://") or str(LEADS_DB).startswith("postgres://"):
        return psycopg2.connect(LEADS_DB), True
    else:
        db_path = os.path.join('/tmp', os.path.basename(LEADS_DB)) if os.environ.get('VERCEL') else LEADS_DB
        return sqlite3.connect(db_path), False

def init_harvester_db():
    conn, is_postgres = get_db_connection()
    cursor = conn.cursor()

    if is_postgres:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                property_type TEXT,
                location TEXT,
                price_ngn REAL,
                contact_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
        cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS business_name TEXT")
        cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS category TEXT")
        cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS email TEXT")
        cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone TEXT")
        cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS source_url TEXT")
        cursor.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS harvested_at TIMESTAMPTZ")
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT,
                category TEXT,
                email TEXT,
                phone TEXT,
                harvested_at TEXT
            )''')
        cursor.execute("PRAGMA table_info(leads)")
        existing_cols = [col[1] for col in cursor.fetchall()]
        
        for col in ["property_type", "location", "contact_info", "created_at", "email", "phone", "source_url"]:
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE leads ADD COLUMN {col} TEXT")
        if "price_ngn" not in existing_cols:
            cursor.execute("ALTER TABLE leads ADD COLUMN price_ngn REAL")
            
    conn.commit()
    cursor.close()
    conn.close()

# --- Utility Functions ---
def is_valid_email(email):
    """Regex to validate proper email structure before DB insertion."""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, str(email).strip()) is not None

def send_discord_alert(webhook_url, title, description, color, fields=None, url=None):
    """Pushes a dynamically formatted payload to a specific Discord webhook channel."""
    if not webhook_url:
        return
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {"text": "Zannie Market Intelligence Engine"}
    }
    
    if fields:
        embed["fields"] = fields
    if url and url.startswith("http"):
        embed["url"] = url
        
    data = {
        "username": "Zannie Harvester",
        "embeds": [embed]
    }
    
    try:
        requests.post(webhook_url, json=data, timeout=5)
    except Exception as e:
        print(f"Webhook push failed: {e}")

# --- Routes ---
@harvester_bp.route("/leads", methods=["GET"])
def base_redirect():
    return redirect("/harvester/corporate")

@harvester_bp.route("/corporate", methods=["GET"])
def view_corporate_leads():
    try:
        init_harvester_db()
        conn, is_postgres = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, business_name, category, email, phone, source_url, COALESCE(harvested_at::text, 'Recent')
            FROM leads WHERE business_name IS NOT NULL ORDER BY id DESC
        """ if is_postgres else """
            SELECT id, business_name, category, email, phone, source_url, harvested_at
            FROM leads WHERE business_name IS NOT NULL ORDER BY id DESC
        """
        cursor.execute(query)
        leads_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("harvester_corporate.html", leads=leads_data)
    except Exception as e:
        return f"Database connectivity fault: {e}", 500

@harvester_bp.route("/properties", methods=["GET"])
def view_property_leads():
    try:
        init_harvester_db()
        conn, is_postgres = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, property_type, location, price_ngn, email, phone, source_url, COALESCE(created_at::text, 'Recent')
            FROM leads WHERE property_type IS NOT NULL ORDER BY id DESC
        """ if is_postgres else """
            SELECT id, property_type, location, price_ngn, email, phone, source_url, created_at
            FROM leads WHERE property_type IS NOT NULL ORDER BY id DESC
        """
        cursor.execute(query)
        leads_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("harvester_properties.html", leads=leads_data)
    except Exception as e:
        return f"Database connectivity fault: {e}", 500

@harvester_bp.route("/leads/ingest", methods=["POST"])
def ingest_lead():
    try:
        data = request.get_json()
        init_harvester_db()
        conn, is_postgres = get_db_connection()
        cursor = conn.cursor()
        
        param = "%s" if is_postgres else "?"
        tstamp = datetime.now() if is_postgres else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Clean and Validate Email Pipeline
        raw_email = data.get('email')
        clean_email = raw_email if is_valid_email(raw_email) else None
        
        phone = data.get('phone')
        source_url = data.get('source_url')
        
        if 'property_type' in data:
            prop_type = data.get('property_type')
            loc = data.get('location')
            new_price = data.get('price_ngn')
            
            # 2. Price Drop Assessment & Upsert Logic
            if source_url:
                cursor.execute(f"SELECT id, price_ngn FROM leads WHERE source_url = {param}", (source_url,))
                existing_record = cursor.fetchone()
                
                if existing_record:
                    old_id, old_price = existing_record
                    
                    # Trigger alerts if the new scraped price is lower than the database price
                    if new_price and old_price and float(new_price) < float(old_price):
                        drop = float(old_price) - float(new_price)
                        
                        # A. Private / Premium Alert (Unmasked Data)
                        private_fields = [
                            {"name": "Asset", "value": prop_type, "inline": False},
                            {"name": "Old Price", "value": f"₦{float(old_price):,.2f}", "inline": True},
                            {"name": "New Price", "value": f"₦{float(new_price):,.2f}", "inline": True},
                            {"name": "Total Drop", "value": f"₦{drop:,.2f}", "inline": False},
                            {"name": "Verified Email", "value": clean_email or "None", "inline": True},
                            {"name": "Direct Phone", "value": phone or "None", "inline": True}
                        ]
                        send_discord_alert(
                            PRIVATE_WEBHOOK_URL, 
                            "🔥 PREMIUM MARKET BREAK: Price Drop!", 
                            f"Price cut detected in **{loc}**.", 
                            0x2ea043, # Green
                            private_fields, 
                            source_url
                        )

                        # B. Public / Freemium Alert (Masked Data)
                        public_fields = [
                            {"name": "Asset", "value": prop_type, "inline": False},
                            {"name": "Old Price", "value": f"₦{float(old_price):,.2f}", "inline": True},
                            {"name": "New Price", "value": f"₦{float(new_price):,.2f}", "inline": True},
                            {"name": "Total Drop", "value": f"₦{drop:,.2f}", "inline": False},
                            {"name": "Contact Agent", "value": "🔒 Locked (Premium Members Only)", "inline": False}
                        ]
                        send_discord_alert(
                            PUBLIC_WEBHOOK_URL, 
                            "📉 Price Drop Alert!", 
                            f"A property in **{loc}** just got cheaper! Upgrade to VIP to access direct agent lines.", 
                            0xe36209, # Orange
                            public_fields,
                            source_url
                        )

                    # Update the existing DB record instead of creating duplicates
                    cursor.execute(f"""
                        UPDATE leads
                        SET price_ngn = {param}, email = {param}, phone = {param}, created_at = {param}
                        WHERE id = {param}
                    """, (new_price, clean_email, phone, tstamp, old_id))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return jsonify({"status": "success", "message": "Existing property updated."}), 200
            
            # Normal insertion if it's a completely new property
            cursor.execute(f"""
                INSERT INTO leads (property_type, location, price_ngn, email, phone, source_url, created_at)
                VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param})""",
                (prop_type, loc, new_price, clean_email, phone, source_url, tstamp))
            
            # Broadcast new discovery to the public channel (Teaser)
            teaser_fields = [
                {"name": "Location", "value": loc, "inline": True},
                {"name": "Valuation", "value": f"₦{float(new_price):,.2f}", "inline": True},
                {"name": "Deal Direct Line", "value": "🔒 Hidden — Subscribe to View", "inline": False}
            ]
            send_discord_alert(
                PUBLIC_WEBHOOK_URL, 
                "✨ New Listing Discovered", 
                f"New **{prop_type}** logged into the pipeline.", 
                0x3182ce, # Blue
                teaser_fields,
                source_url
            )

        else:
            # Normal insertion for Corporate Intel (respects the DB abstraction and email filter)
            cursor.execute(f"""
                INSERT INTO leads (business_name, category, email, phone, source_url, harvested_at)
                VALUES ({param}, {param}, {param}, {param}, {param}, {param})""",
               (data.get('business_name'), data.get('category'), clean_email, phone, source_url, tstamp))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Data ingested seamlessly."}), 201
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
