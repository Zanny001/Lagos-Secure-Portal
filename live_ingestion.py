import sqlite3
import time
import requests
import re
import csv
from bs4 import BeautifulSoup
from random import randint

DB_PATH = "lagos_leads.db"
CSV_OUTPUT_PATH = "lagos_premium_leads.csv"

def init_database():
    """Initializes the local relational SQLite cluster for scraped leads."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT,
            category TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            harvested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead_safely(lead_data):
    """Inserts freshly processed leads, safely ignoring duplicate email conflicts."""
    query = """
        INSERT OR IGNORE INTO leads (business_name, category, email, phone)
        VALUES (?, ?, ?, ?)
    """
    try:
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute(query, lead_data)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"🎯 [DATABASE] Saved Hiring Lead: {lead_data[0]} | {lead_data[2]}")
    except Exception as e:
        pass

def export_database_to_csv():
    """Compiles all stored leads from the database out to a production CSV lead sheet."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT business_name, category, email, phone FROM leads")
            rows = cursor.fetchall()
            if not rows:
                print("\n[EXPORT WARNING] No records found inside the database yet.")
                return

            with open(CSV_OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Company Name", "Category", "Contact Email", "Target Title / Phone"])
                writer.writerows(rows)
                print(f"\n🎉 [SUCCESS] Lead pack generated! {len(rows)} rows compiled inside {CSV_OUTPUT_PATH}.")
    except Exception as e:
        print(f"[EXPORT ERROR] {e}")

def scrape_hiring_leads(url):
    """Parses live HTML stream headers from regional job streams to ingest target contacts."""
    print(f"\n[HARVEST] Ingesting public stream layer -> {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[WARNING] Status offline: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        # Target MyJobMag's specific structural li elements containing listings
        items = soup.find_all('li', class_=re.compile(r'(?:job-item|job-list|mag-list|item)', re.I))
        if not items:
            items = soup.find_all(['li', 'div'], class_='mag-list')

        for item in items:
            # Locate the specific anchor tag holding corporate name details
            company_element = item.find('a', href=re.compile(r'/jobs-at/'))
            title_element = item.find(['h2', 'h3', 'a'], class_=re.compile(r'(?:job-title|title)', re.I))

            if company_element and title_element:
                company_raw = company_element.get_text().strip()
                title_raw = title_element.get_text().strip()

                # Strip out common noisy sub-strings if they bleed through
                company_clean = re.split(r'(?:\bby\b|\bat\b|Description|\bWe are\b|Role|Job|Salary)', company_raw, flags=re.I)[0].strip()
                company_clean = re.sub(r'\s+', ' ', company_clean)

                # Guardrails for length verification
                if len(company_clean) > 45 or len(company_clean) < 3 or "Jobs" in company_clean:
                    continue

                # Build target corporate email guess formats
                domain_slug = company_clean.lower()
                domain_slug = re.sub(r'[^a-z0-9]', '', domain_slug.replace("limited", "").replace("ltd", ""))
                mock_email = f"hr@{domain_slug}.com.ng"
                save_lead_safely((company_clean, "Hiring Company (Lagos)", mock_email, title_raw))

            else:
                # Fallback to text content processing regex if specific classes aren't hit
                text_content = item.get_text(" ")
                name_match = re.search(r'([A-Za-z0-9\s&]+)\sat\s([A-Za-z0-9\s&.\-]+)', text_content)
                if name_match:
                    title = name_match.group(1).strip()
                    company = name_match.group(2).strip().split("\n")[0]
                    company_clean = re.split(r'(?:Description|\bWe are\b|\bWork\b|Salary)', company, flags=re.I)[0].strip()

                    if len(company_clean) > 45 or "Jobs" in company_clean or len(company_clean) < 4:
                        continue

                    domain_slug = re.sub(r'[^a-z0-9]', '', company_clean.lower().replace("limited", "").replace("ltd", "").replace(" ", ""))
                    mock_email = f"hr@{domain_slug}.com.ng"
                    save_lead_safely((company_clean, "Hiring Company (Lagos)", mock_email, title))

    except Exception as e:
        print(f"[ERROR] Parsing exception: {e}")

if __name__ == "__main__":
    print("=====================================================")
    print("      LAGOS HARVESTER: INGESTION PIPELINE ONLINE     ")
    print("=====================================================")
    init_database()
    targets = [
        "https://www.myjobmag.com/jobs-location/lagos",
        "https://www.myjobmag.com/cp/online-jobs-lagos",
        "https://www.myjobmag.com/jobs-city/lagos-island"
    ]

    for url in targets:
        scrape_hiring_leads(url)
        time.sleep(randint(3, 5))

    export_database_to_csv()
    print("[COMPLETE] Engine shut down successfully.")
