import os
import re
import time
import sqlite3
import urllib.request
from bs4 import BeautifulSoup

# Standardized browser agent signature to prevent firewall blocks
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
)

def extract_numeric_price(price_text):
    """Removes currency symbols and returns clean float values."""
    cleaned = re.sub(r'[^\d]', '', price_text)
    return float(cleaned) if cleaned else 0.0

def commit_to_database(location, price):
    """
    Ingests raw parsed metrics into the active SQLite tracking database,
    triggering analytics summary updates.
    """
    db_name = "realestate_analytics.db"
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # 1. Log individual raw listing entry
        cursor.execute(
            "INSERT INTO listings (location, price) VALUES (?, ?)",
            (location, price)
        )
        
        # 2. Compute live aggregates across the database node for the location
        cursor.execute(
            "SELECT COUNT(*), AVG(price) FROM listings WHERE location = ?",
            (location,)
        )
        total_listings, average_price = cursor.fetchone()
        
        # 3. Upsert atomic summary metrics into cache table
        cursor.execute('''
            INSERT INTO analytics_summary (location, total_listings, average_price_ngn, last_updated)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
            ON CONFLICT(location) DO UPDATE SET
                total_listings = excluded.total_listings,
                average_price_ngn = excluded.average_price_ngn,
                last_updated = excluded.last_updated
        ''', (location, total_listings, average_price))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[DATABASE ERROR] Ingestion worker transaction failure: {e}")
        return False

def crawl_paginated_market(max_pages=3):
    """
    Iterates sequentially through multiple web listing pages, injecting
    custom headers to bypass basic anti-scraping filters.
    """
    print(f"Starting Multi-Page Web Crawl (Limit: {max_pages} pages)...")
    
    # Points cleanly to your local Python server file
    base_url = "http://127.0.0.1:8080/listings.html"
    
    for page_num in range(1, max_pages + 1):
        # Append pagination query parameters dynamically
        target_url = f"{base_url}?page={page_num}"
        print(f"\n[CRAWLER] Fetching page {page_num}/{max_pages}: {target_url}")
        
        # Configure request container with browser headers
        req = urllib.request.Request(
            target_url, 
            headers={'User-Agent': BROWSER_USER_AGENT}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            cards = soup.find_all('div', class_='property-listing-card')
            
            if not cards:
                print(f"[CRAWLER] No listing elements found on page {page_num}. Ending loop.")
                break
                
            print(f"[CRAWLER] Successfully extracted {len(cards)} listings from page content.")
            
            # Loop through each item card structure on the current page
            for card in cards:
                location_el = card.find('span', class_='location')
                price_el = card.find('span', class_='price')
                
                if location_el and price_el:
                    loc = location_el.text.strip()
                    raw_price = price_el.text.strip()
                    numeric_price = extract_numeric_price(raw_price)
                    
                    # Push directly into data analytics storage layers
                    success = commit_to_database(loc, numeric_price)
                    if success:
                        print(f"   [DB SUCCESS] Saved: {loc} | ₦{numeric_price:,.2f}")
            
        except urllib.error.URLError as e:
            print(f"[CRAWLER ERROR] HTTP Request failed on page {page_num}: {e.reason}")
        except Exception as e:
            print(f"[CRAWLER ERROR] Unexpected parsing error: {e}")
            
        # Standard safety delay throttle to protect hosting endpoints
        time.sleep(2)
        
    print("\n[CRAWLER COMPLETE] Multi-page scraping operations completed cleanly.")

if __name__ == "__main__":
    crawl_paginated_market()

