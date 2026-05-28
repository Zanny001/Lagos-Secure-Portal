import time
from pipeline import init_database, save_leads_batch

def simulate_web_scraper():
    init_database()
    target_pages = ["page_1", "page_2", "page_3"]
    
    # Infinite polling structure to keep process persistent on your dashboard
    while True:
        print(f"\n[TIME CHECK] Ingestion cycle started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        for page in target_pages:
            print(f"[NETWORK] Ingesting unparsed HTML components from: {page}...")
            
            raw_scraped_buffer = [
                ("Zannie Fashion Hub", "0803 123 4567", "Ikeja, Lagos", "Fashion"),
                ("Lagos Tech Ventures", "+234-815-999-8888", "Yaba, Lagos", "Technology"),
                ("Alaba Logistics Group", "09011223344", "Alaba, Ojo", "Logistics")
            ]
            
            rows_inserted = save_leads_batch(raw_scraped_buffer)
            print(f"[SUCCESS] Safely committed {rows_inserted} unique business structures from {page}.")
            time.sleep(0.5)
            
        print("[IDLE] Cycle finished. Sleeping background thread for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    simulate_web_scraper()
