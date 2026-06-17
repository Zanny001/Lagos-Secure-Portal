import time
import urllib.request
import urllib.error
import re
from pipeline import init_database, save_leads_batch

def fetch_web_page(url):
    """
    Fetches raw HTML layout text string over the network using native utilities.
    Includes an explicit mobile user-agent header to pass security boundaries safely.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except urllib.error.URLError as e:
        print(f"[NETWORK ERROR] Failed to pull target destination: {e.reason}")
    except Exception as e:
        print(f"[UNKNOWN FAULT] Network connection interrupted: {e}")
    return None

def extract_leads_from_html(html_content, category="General Business"):
    """
    Parses unformatted HTML stream textures using high-speed matching blocks.
    Captures company names from heading boundaries and isolates raw phone chains.
    """
    extracted_buffer = []

    # Structural Pattern Block Matcher: Looks for business cards or heading layouts
    name_pattern = re.compile(r'(?:class="biz-name"|itemprop="name")[^>]*>([^<]+)</', re.IGNORECASE)
    phone_pattern = re.compile(r'(?:class="phone"|itemprop="telephone")[^>]*>([^<]+)</', re.IGNORECASE)
    address_pattern = re.compile(r'(?:class="address"|itemprop="address")[^>]*>([^<]+)</', re.IGNORECASE)

    companies = name_pattern.findall(html_content)
    phones = phone_pattern.findall(html_content)
    addresses = address_pattern.findall(html_content)

    for i in range(min(len(companies), len(phones))):
        name = companies[i].strip()
        raw_phone = phones[i].strip()
        addr = addresses[i].strip() if i < len(addresses) else "Lagos, Nigeria"

        extracted_buffer.append((name, raw_phone, addr, category))

    return extracted_buffer

def simulate_web_scraper():
    print("[START] Launching Automated Lagos Harvester Service Engine...")
    init_database()
    
    # Core targeting configuration array (Points to live testing directory site)
    target_targets = [
        {"url": "https://quotes.toscrape.com", "cat": "Business Inbound"},
    ]

    # Infinite polling structure to keep process persistent on your dashboard
    while True:
        print(f"\n[TIME CHECK] Ingestion cycle started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for target in target_targets:
            print(f"[NETWORK] Connecting to target boundary line: {target['url']}...")
            html_data = fetch_web_page(target['url'])
            
            if not html_data:
                print("[SKIPPED] Continuing loop due to empty network data stream.")
                continue
                
            # Parse real text matrix strings out 
            raw_leads = extract_leads_from_html(html_data, category=target['cat'])
            print(f"[PARSED] Discovered {len(raw_leads)} structural element signatures in raw source markup.")
            
            # Ship to pipeline database buffer processing layer
            rows_inserted = save_leads_batch(raw_leads)
            print(f"[SUCCESS] Safely committed {rows_inserted} unique business structures from target.")
            
            # Polyphase throttle pacing to respect remote servers
            time.sleep(2.0)

        print("[IDLE] Cycle finished. Sleeping background thread for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    simulate_web_scraper()

