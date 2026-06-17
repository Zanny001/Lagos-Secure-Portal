import sqlite3
import time
import requests
from datetime import datetime

# Configuration Settings
SPORTS_DB = "sports_analytics.db"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/mock_crypto_channel_token"

def init_sports_database():
    """Initializes persistent storage blocks for structural odds history tracking."""
    with sqlite3.connect(SPORTS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS odds_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                home_team TEXT,
                away_team TEXT,
                outcome_name TEXT,
                recorded_price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def track_odds_drift(match_id, outcome_name, current_price):
    """
    Queries previous historical table snapshots to compute percentage drift alterations.
    Returns the computed percentage shift if a historical data anchor exists.
    """
    with sqlite3.connect(SPORTS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT recorded_price FROM odds_history 
            WHERE match_id = ? AND outcome_name = ? 
            ORDER BY id DESC LIMIT 1
        """, (match_id, outcome_name))
        row = cursor.fetchone()
        
        if row:
            previous_price = row[0]
            if previous_price > 0:
                drift_pct = ((current_price - previous_price) / previous_price) * 100
                return drift_pct
        return 0.0

def save_odds_snapshot(match_id, home, away, outcome_name, price):
    """Commits individual market price nodes directly to local relational records."""
    with sqlite3.connect(SPORTS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO odds_history (match_id, home_team, away_team, outcome_name, recorded_price)
            VALUES (?, ?, ?, ?, ?)
        """, (match_id, home, away, outcome_name, price))
        conn.commit()

def fetch_live_fixtures():
    """Simulates real-time market data retrieval matrices for high-tier football."""
    # Mocking live incoming odds feed updates for match evaluations
    # In production, this pulls straight from external developer feed endpoints
    return [
        {
            "id": "match_manutd_realmadrid_2026",
            "home_team": "Manchester United",
            "away_team": "Real Madrid",
            "bookmakers": [{
                "key": "bet365",
                "title": "Bet365",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Manchester United", "price": 2.55}, # Price shifted up from 2.45
                        {"name": "Real Madrid", "price": 2.60},
                        {"name": "Draw", "price": 3.25}
                    ]
                }]
            }]
        }
    ]

def evaluate_and_process_sports_data():
    fixtures = fetch_live_fixtures()
    
    for match in fixtures:
        match_id = match.get("id")
        home = match.get("home_team")
        away = match.get("away_team")
        bookmaker = match.get("bookmakers", [{}])[0]
        outcomes = bookmaker.get("markets", [{}])[0].get("outcomes", [])
        
        significant_shift_detected = False
        embed_fields = []
        
        print(f"\n[ANALYTICS ENGINE] Evaluating Matchup: {home} vs {away}")
        
        for outcome in outcomes:
            name = outcome["name"]
            current_price = outcome["price"]
            
            # Calculate drift variance compared to last known entry
            drift = track_odds_drift(match_id, name, current_price)
            
            # Commit the new baseline value immediately to the tracking array
            save_odds_snapshot(match_id, home, away, name, current_price)
            
            # Flag shifts greater than 2% for notifications
            drift_direction = "🔺" if drift > 0 else "🔻"
            drift_str = f" ({drift_direction} {abs(drift):.1f}%)" if abs(drift) > 0 else " (Stable)"
            
            print(f" -> Market Line: {name} | Odds: {current_price}{drift_str}")
            
            embed_fields.append({
                "name": f"🔹 {name}",
                "value": f"Current Odds: `{current_price}`\nDrift Variance: `{drift_direction} {drift:.2f}%`" if abs(drift) > 0 else f"Current Odds: `{current_price}`\nDrift Variance: `0.00% (No Drift)`",
                "inline": True
            })
            
            if abs(drift) >= 2.0:
                significant_shift_detected = True

        # Dispatch alert updates only if a significant market shift occurs
        if significant_shift_detected:
            print(f"[ALERTS FEED] Sharp odds drift detected! Routing update notification...")
            payload = {
                "embeds": [{
                    "title": "🚨 MARKET DRIFT DETECTED: LIVE ODDS UPDATE",
                    "color": 16724016, # Alert Crimson Red
                    "description": f"Significant market shifts processed from **{bookmaker.get('title')}**.",
                    "fields": [
                        {"name": "Matchup", "value": f"⚽ **{home}** vs **{away}**", "inline": False}
                    ] + embed_fields,
                    "footer": {"text": "Zannie Brand Real-Time Sports Analytics Core"},
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }]
            }
            try:
                requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
            except Exception as e:
                print(f"[ERROR] Failed to push alert webhook: {e}")

def run_sports_ticker_loop():
    print("==========================================================")
    print("🛰️ ASYNCHRONOUS DATA-BACKED SPORTS TICKER ONLINE")
    print("==========================================================")
    init_sports_database()
    
    while True:
        try:
            evaluate_and_process_sports_data()
        except Exception as e:
            print(f"[SPORTS WORKER ERROR] Loop failure: {e}")
            
        time.sleep(300) # Re-evaluate every 5 minutes

if __name__ == "__main__":
    run_sports_ticker_loop()

