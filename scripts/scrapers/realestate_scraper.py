import os
import re
import requests
from bs4 import BeautifulSoup

# The exact endpoint defined in your Flask app
API_ENDPOINT = "http://127.0.0.1:5001/harvester/leads/ingest"

# --- THE UPGRADE: Authentication & Session Headers ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Paste your active session cookie below if you hit a login wall
    "Cookie": "PHPSESSID=your_extracted_session_cookie_here;" 
}

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
    </body>
</html>
"""

def extract_clean_numeric_price(price_text):
    """Cleans raw web strings like '₦ 120,000,000' into standard database floats."""
    cleaned = re.sub(r'[^\d]', '', price_text)
    return float(cleaned) if cleaned else 0.0

def push_to_pipeline(prop_type, loc, price_ngn, contact_info, source_url):
    """Packages the scraped data into the exact JSON format your Flask API expects."""
    phone_match = re.search(r'0[789][01]\d{8}', contact_info)
    phone = phone_match.group(0) if phone_match else contact_info

    payload = {
        "property_type": prop_type,
        "location": loc,
        "price_ngn": price_ngn,
        "phone": phone,
        "email": "agent@zannie.com", 
        "source_url": source_url
    }

    try:
        res = requests.post(API_ENDPOINT, json=payload, timeout=5)
        print(f"[API PUSH] Status {res.status_code} | {prop_type} -> Pipeline synchronized.")
    except Exception as e:
        print(f"[API ERROR] Failed to hit local Flask endpoint: {e}")

def fetch_live_page(target_url):
    """Fetches real HTML from the target site using our auth headers."""
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[NETWORK ERROR] Could not fetch live page: {e}")
        return None

def run_scraper_extraction(use_live_data=False, target_url=""):
    """Parses structural HTML and passes elements down the API pipeline."""
    print("Initializing parsing matrix on structural web assets...")
    
    if use_live_data and target_url:
        html_content = fetch_live_page(target_url)
        if not html_content:
            return
    else:
        html_content = MOCK_WEB_PAGE_HTML

    soup = BeautifulSoup(html_content, 'html.parser')

    # Update these class names when targeting the live website's structure
    cards = soup.find_all('div', class_='property-listing-card')
    print(f"Identified {len(cards)} data elements for processing.\n")

    for i, card in enumerate(cards):
        title_element = card.find('h2', class_='listing-title')
        zone_element = card.find('p', class_='listing-zone')
        price_element = card.find('span', class_='price-tag')
        contact_element = card.find('div', class_='agent-contact')

        if title_element and zone_element and price_element:
            property_type = title_element.text.strip()
            location = zone_element.text.strip()
            raw_price = price_element.text.strip()
            contact_info = contact_element.text.replace('Contact:', '').strip() if contact_element else "N/A"

            price_ngn = extract_clean_numeric_price(raw_price)
            mock_source_url = f"https://www.propertypro.ng/listing/zannie-mock-prop-{i+1}"

            push_to_pipeline(property_type, location, price_ngn, contact_info, mock_source_url)

if __name__ == "__main__":
    # Toggle 'use_live_data=True' and provide the real URL when you are ready to hit the live site
    run_scraper_extraction(use_live_data=False)

