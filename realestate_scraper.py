import os
import re
import sqlite3
from bs4 import BeautifulSoup

# Import your existing pipeline insertion logic
try:
    from run_pipeline import insert_and_sync_lead
except ImportError:
    # Fallback inline function if run_pipeline is in a different path context
    def insert_and_sync_lead(prop_type, loc, price, contact):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'realestate_analytics.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (property_type, location, price_ngn, contact_info)
            VALUES (?, ?, ?, ?)
        ''', (prop_type, loc, price, contact))
        conn.commit()
        conn.close()
        print(f"[FALLBACK INGEST] Logged: {prop_type} in {loc}")

# Mock HTML simulation layout matching public real estate listings structure
MOCK_WEB_PAGE_HTML = """
<html>
    <body>
        <div class="property-listing-card">
            <h2 class="listing-title">Luxury 4 Bedroom Detached Duplex</h2>
            <p class="listing-zone">Lekki, Lagos</p>
            <span class="price-tag">₦ 120,000,000</span>
            <div class="agent-contact">Contact: 08031112233 - Ref: ZN-09</div>
        </div>
        <div class="property-listing-card">
            <h2 class="listing-title">Fully Serviced 3 Bedroom Apartment</h2>
            <p class="listing-zone">Ikoyi, Lagos</p>
            <span class="price-tag">₦ 195,000,000</span>
            <div class="agent-contact">Contact: 08034445566 - Ref: ZN-12</div>
        </div>
        <div class="property-listing-card">
            <h2 class="listing-title">Commercial Office Space Block</h2>
            <p class="listing-zone">Ikeja, Lagos</p>
            <span class="price-tag">₦ 210,000,000</span>
            <div class="agent-contact">Contact: 08037778899 - Ref: ZN-44</div>
        </div>
    </body>
</html>
"""

def extract_clean_numeric_price(price_text):
    """
    Cleans raw web strings like '₦ 120,000,000' into standard database floats.
    """
    cleaned = re.sub(r'[^\d]', '', price_text)
    return float(cleaned) if cleaned else 0.0

def run_scraper_extraction():
    """
    Parses structural HTML layouts, extracts data primitives, 
    and passes them cleanly down to the database infrastructure layer.
    """
    print("Initializing parsing matrix on structural web assets...")
    soup = BeautifulSoup(MOCK_WEB_PAGE_HTML, 'html.parser')
    
    cards = soup.find_all('div', class_='property-listing-card')
    print(f"Identified {len(cards)} data elements for processing.\n")
    
    for card in cards:
        # Extract fields using BeautifulSoup selectors
        title_element = card.find('h2', class_='listing-title')
        zone_element = card.find('p', class_='listing-zone')
        price_element = card.find('span', class_='price-tag')
        contact_element = card.find('div', class_='agent-contact')
        
        if title_element and zone_element and price_element:
            property_type = title_element.text.strip()
            location = zone_element.text.strip()
            raw_price = price_element.text.strip()
            contact_info = contact_element.text.replace('Contact:', '').strip() if contact_element else "N/A"
            
            # Clean text price down to structural floats
            price_ngn = extract_clean_numeric_price(raw_price)
            
            # Commit the harvested row downstream into the database pipeline
            insert_and_sync_lead(property_type, location, price_ngn, contact_info)

if __name__ == "__main__":
    run_scraper_extraction()

