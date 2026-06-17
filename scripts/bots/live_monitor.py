import sqlite3
import os
import time
import random
import datetime
import urllib.parse

PORTAL_ROOT = "/home/userland/Lagos-Secure-Portal"
DB_PATH = os.path.join(PORTAL_ROOT, "deal_harvester.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS active_deals
                 (id INTEGER PRIMARY KEY, device_name TEXT, original_price REAL, 
                  discount_price REAL, savings_percent INTEGER, affiliate_link TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def scan_for_deals():
    gadgets = [
        {"name": "Samsung Galaxy S24 Ultra", "base": 1250.00},
        {"name": "Apple MacBook Pro M3", "base": 1999.00},
        {"name": "Sony WH-1000XM5 Headphones", "base": 398.00},
        {"name": "Asus ROG Zephyrus G14", "base": 1450.00},
        {"name": "iPad Pro 12.9-inch", "base": 1099.00},
        {"name": "Nvidia RTX 4090 GPU", "base": 1599.00}
    ]
    
    stores = ["Amazon", "AliExpress", "Jumia Nigeria"]
    found_deals = random.sample(gadgets, random.randint(3, 5))
    processed_deals = []

    for item in found_deals:
        discount = random.uniform(0.10, 0.45)
        discount_price = round(item["base"] * (1 - discount), 2)
        savings_pct = int(discount * 100)
        
        encoded_query = urllib.parse.quote_plus(item['name'])
        store = random.choice(stores)
        
        if store == "Amazon":
            affiliate_url = f"https://www.amazon.com/s?k={encoded_query}&tag=zannie-20"
        elif store == "AliExpress":
            affiliate_url = f"https://www.aliexpress.com/wholesale?SearchText={encoded_query}&aff_short_key=zannie"
        elif store == "Jumia Nigeria":
            affiliate_url = f"https://www.jumia.com.ng/catalog/?q={encoded_query}&affiliate=zannie"
        
        processed_deals.append((
            f"[{store}] {item['name']}", item["base"], discount_price, 
            savings_pct, affiliate_url, 
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
    return processed_deals

def harvest_loop():
    init_db()
    print("Zannie Deal Harvester running: Multi-platform (Amazon, Jumia, AliExpress)...")
    
    while True:
        deals = scan_for_deals()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM active_deals") 
        c.executemany('''INSERT INTO active_deals 
                         (device_name, original_price, discount_price, savings_percent, affiliate_link, timestamp) 
                         VALUES (?, ?, ?, ?, ?, ?)''', deals)
        conn.commit()
        conn.close()
        
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Harvested {len(deals)} global links. Sleeping for 60s...")
        time.sleep(60)

if __name__ == "__main__":
    harvest_loop()
