import hmac
import hashlib
import json
import requests

# 1. This MUST match the secret key token inside your zannie_brand.py script
PAYSTACK_WEBHOOK_SECRET = "whsec_your_zannie_brand_secret_token"

# 2. Define the public URL endpoint routing down your tunnel
TARGET_URL = "https://fifty-salvage-starring.ngrok-free.dev/api/v1/payments/webhook"

def send_signed_mock_payment():
    # 3. Formulate the precise payment payload payload dictionary structure
    mock_payload = {
        "event": "charge.success",
        "data": {
            "amount": 1275000,  # 12,750.00 in minor units (e.g., Kobo)
            "currency": "NGN",
            "reference": "ZNY_REF_B65214_Y",
            "customer": {
                "email": "lux_buyer@zannie-footwear.com"
            }
        }
    }
    
    # 4. Serialize the dictionary payload strictly into a raw string bytes layout
    raw_payload_bytes = json.dumps(mock_payload, separators=(',', ':')).encode('utf-8')
    
    # 5. Compute the exact HMAC-SHA512 hex signature verification hash
    computed_signature = hmac.new(
        key=PAYSTACK_WEBHOOK_SECRET.encode('utf-8'),
        msg=raw_payload_bytes,
        digestmod=hashlib.sha512
    ).hexdigest()
    
    # 6. Configure network delivery headers including the authenticated signature
    headers = {
        "Content-Type": "application/json",
        "x-paystack-signature": computed_signature
    }
    
    print(f"[SIMULATOR] Dispatched signed data package over tunnel payload...")
    
    try:
        # 7. Post the data payload packet over the public ngrok lines
        response = requests.post(TARGET_URL, data=raw_payload_bytes, headers=headers, timeout=10)
        print(f"[SIMULATOR] Server Response Status Code: {response.status_code}")
        print(f"[SIMULATOR] Server Body Output: {response.text}")
    except Exception as e:
        print(f"[SIMULATOR ERROR] Network dispatch failed: {e}")

if __name__ == "__main__":
    send_signed_mock_payment()

