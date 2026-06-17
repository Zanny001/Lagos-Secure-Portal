import requests
import json

url = "http://127.0.0.1:5001/zannie/api/orders/create"
payload = {
    "customer_name": "Alabi Kunle",
    "customer_email": "kunle@lagosdesign.ng",
    "customer_phone": "+2348123456789",
    "garment_name": "Premium Cashmere Agbada Set",
    "base_price_ngn": 185000.00,
    "fabric_matrix": "Super-140s Imported Cashmere Blend",
    "embroidery_profile": "Traditional Geometric Heavy Stitch"
}

headers = {
    "Content-Type": "application/json"
}

try:
    print("[*] Dispatching order initialization packet directly to server...")
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    print(f"[+] Server Response Status: {response.status_code}")
    print(f"[+] Output Payload: {response.text}")
except Exception as e:
    print(f"[-] Local Network Failure: {str(e)}")
