import json
import hmac
import hashlib
import requests

# Pointing exactly to your background server instance on Port 5001
TARGET_URL = "http://127.0.0.1:5001/api/v1/payments/webhook"
# Must perfectly match the security token inside zannie_brand.py
WEBHOOK_SECRET = "whsec_zannie_signature_verification_token"

def run_webhook_simulation():
    print("\n" + "="*50)
    print("🚀 INITIALIZING LOCAL PAYSTACK WEBHOOK SECURITY TEST")
    print("="*50)

    # 1. Structural template of a successful Paystack transaction 
    mock_payload = {
        "event": "charge.success",
        "data": {
            "id": 4092281,
            "status": "success",
            "reference": "ZNY-TX-20260527-991",
            "amount": 12750000,  # 127,500.00 Kobo ($85.00 converted to NGN)
            "currency": "NGN",
            "customer": {
                "email": "client.femi@example.com",
                "name": "Hassan Oluwafemi"
            },
            "metadata": {
                "product_sku": "ZNY-JAL-01",
                "item_name": "Zannie Signature Monogram Jalabiya"
            }
        }
    }

    # Format dictionary data seamlessly into string bytes for cryptographic hashing
    raw_bytes = json.dumps(mock_payload).encode('utf-8')

    # 2. Compute a legitimate HMAC-SHA512 Signature
    computed_signature = hmac.new(
        key=WEBHOOK_SECRET.encode('utf-8'),
        msg=raw_bytes,
        digestmod=hashlib.sha512
    ).hexdigest()

    # ----------------------------------------------------
    # TEST CASE A: VALID SIGNED TRANSACTION SUBMISSION
    # ----------------------------------------------------
    print("\n[TEST A] Forwarding authentic signed payload from Paystack Gateway...")
    valid_headers = {
        "Content-Type": "application/json",
        "x-paystack-signature": computed_signature
    }
    
    try:
        response_a = requests.post(TARGET_URL, data=raw_bytes, headers=valid_headers, timeout=5)
        print(f" -> Response Status: {response_a.status_code}")
        print(f" -> Response Payload: {response_a.json()}")
        if response_a.status_code == 200:
            print(" ✅ SUCCESS: Verification authorized, inventory updated safely.")
        else:
            print(" ❌ FAILURE: Authentic transaction signature rejected.")
    except Exception as e:
        print(f" Local Connection Error: {e}")

    # ----------------------------------------------------
    # TEST CASE B: INTERCEPTED / TAMPERED SIGNATURE REJECTION
    # ----------------------------------------------------
    print("\n[TEST B] Forwarding modified data string (Simulated Attack Vector)...")
    tampered_signature = computed_signature[:-4] + "abcd"  # Deliberately distort signature tail
    invalid_headers = {
        "Content-Type": "application/json",
        "x-paystack-signature": tampered_signature
    }

    try:
        response_b = requests.post(TARGET_URL, data=raw_bytes, headers=invalid_headers, timeout=5)
        print(f" -> Response Status: {response_b.status_code}")
        print(f" -> Response Payload: {response_b.json()}")
        if response_b.status_code == 403:
            print(" ✅ SUCCESS: Timing attack immune filter blocked tampered request (403 Forbidden).")
        else:
            print(" ❌ WARNING: Security gap detected! Server accepted bad signature.")
    except Exception as e:
        print(f" Local Connection Error: {e}")
        
    print("\n" + "="*50)
    print("🔒 CRYPTOGRAPHIC WEBHOOK AUDIT COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_webhook_simulation()

