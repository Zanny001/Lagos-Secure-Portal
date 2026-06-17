import requests
import time

# Target port 5001 where your Flask instance is explicitly listening
API_URL = "http://127.0.0.1:5001/harvester/leads/ingest"

# 1. Simulate the initial listing discovery
initial_payload = {
    "property_type": "4 Bedroom Semi-Detached Duplex",
    "location": "Lekki Phase 1, Lagos",
    "price_ngn": 150000000.00,
    "email": "lekki_sales@zannie.com",
    "phone": "08012345678",
    "source_url": "https://www.propertypro.ng/listing/test-lekki-v2"
}

print("Pushing initial property listing to database...")
res1 = requests.post(API_URL, json=initial_payload)
print(f"Status: {res1.status_code} - {res1.json().get('message', 'No message')}")

print("\nWaiting 3 seconds before simulating a market shift...")
time.sleep(3)

# 2. Simulate a subsequent scrape finding a price drop
drop_payload = {
    "property_type": "4 Bedroom Semi-Detached Duplex",
    "location": "Lekki Phase 1, Lagos",
    "price_ngn": 135000000.00, 
    "email": "lekki_sales@zannie.com",
    "phone": "08012345678",
    "source_url": "https://www.propertypro.ng/listing/test-lekki-v2" 
}

print("Pushing updated price drop (Should trigger Discord webhook)...")
res2 = requests.post(API_URL, json=drop_payload)
print(f"Status: {res2.status_code} - {res2.json().get('message', 'No message')}")
