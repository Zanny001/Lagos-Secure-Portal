import os
import re
import requests
import time
from bs4 import BeautifulSoup

API_ENDPOINT = "http://127.0.0.1:5001/harvester/leads/ingest"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def extract_clean_numeric_price(price_text):
    if not price_text: return 0.0
    is_usd = '$' in price_text or 'USD' in price_text.upper()
    match = re.search(r'[\d,\.]+', price_text)
    if not match: return 0.0
    raw_num_str = match.group(0).replace(',', '').rstrip('.')
    try: numeric_value = float(raw_num_str)
    except ValueError: numeric_value = 0.0
    if is_usd: numeric_value *= 1500.0
    return numeric_value

def fetch_deep_contact_info(source_url):
    try:
        response = requests.get(source_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            phone_match = re.search(r'\b(?:234|0)[789][01]\d{8}\b', response.text)
            if phone_match: return phone_match.group(0)
    except Exception: pass
    return "Contact Not Discovered"

def push_to_pipeline(prop_type, loc, price_ngn, contact_info, source_url):
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
        return True if res.status_code in [200, 201] else False
    except Exception:
        return False

def fetch_live_page(target_url):
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception:
        return None

def run_scraper_extraction(base_url, max_pages=5):
    print("==================================================")
    print(f"[*] INITIALIZING DEEP HARVEST: TARGETING {max_pages} PAGES")
    print("==================================================")
    
    total_harvested = 0
    for page_num in range(1, max_pages + 1):
        target_url = f"{base_url}?page={page_num}" if page_num > 1 else base_url
        print(f"\n[PAGE {page_num}] Scanning Index: {target_url}")
        
        html_content = fetch_live_page(target_url)
        if not html_content: continue
        
        soup = BeautifulSoup(html_content, 'html.parser')
        title_blocks = soup.find_all('div', class_='pl-title')
        if not title_blocks: break
        
        print(f"[*] Identified {len(title_blocks)} blocks. Initiating deep extraction...")
        
        page_success = 0
        for title_block in title_blocks:
            h3_tag = title_block.find('h3')
            a_tag = h3_tag.find('a') if h3_tag else None
            p_tag = title_block.find('p')
            
            parent_box = title_block.find_parent('div')
            price_tag = parent_box.find(class_=re.compile(r'price|listings-price|amt')) if parent_box else None
            
            if a_tag and p_tag:
                property_type = a_tag.text.strip()
                location = p_tag.text.strip()
                raw_url = a_tag['href']
                source_url = raw_url if raw_url.startswith('http') else f"https://www.propertypro.ng{raw_url}"
                
                raw_price = price_tag.text.strip() if price_tag else "₦ 0"
                price_ngn = extract_clean_numeric_price(raw_price)
                
                print(f"    -> Crawling detailed listing: {property_type[:30]}...")
                contact_info = fetch_deep_contact_info(source_url)
                
                success = push_to_pipeline(property_type, location, price_ngn, contact_info, source_url)
                if success:
                    page_success += 1
                    total_harvested += 1
                
                time.sleep(1.5)
        
        print(f"[+] Page {page_num} deep harvest complete.")
        if page_num < max_pages: time.sleep(3)
        
    print("\n==================================================")
    print(f"[*] DEEP HARVEST COMPLETE: {total_harvested} enriched leads saved.")
    print("==================================================")

if __name__ == "__main__":
    LIVE_TARGET_URL = "https://www.propertypro.ng/property-for-sale/in/lagos"
    run_scraper_extraction(base_url=LIVE_TARGET_URL, max_pages=5)
