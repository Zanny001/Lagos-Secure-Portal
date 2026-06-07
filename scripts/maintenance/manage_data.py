import json
import sys
from datetime import datetime

def load_system_config():
    """Reads configuration constants securely from the master JSON registry file."""
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"[CONFIG CRITICAL] Failed to parse config.json registry. Using fallback defaults. Error: {e}")
        return None

# Mock Order Ingestion Database mimicking incoming successful gateway transactions
MOCK_ORDER_LEDGER = [
    {"order_id": "ZNY-2026-001", "email": "buyer1@yaba.ng", "currency": "NGN", "amount_paid": 127500.00, "item": "Signature Monogram Jalabiya", "status": "SUCCESS"},
    {"order_id": "ZNY-2026-002", "email": "intl_client@nyc.com", "currency": "USD", "amount_paid": 85.00, "item": "Zannie Premium Footwear", "status": "SUCCESS"},
    {"order_id": "ZNY-2026-003", "email": "buyer2@ikeja.ng", "currency": "NGN", "amount_paid": 90000.00, "item": "Casual Suede Loafers", "status": "SUCCESS"},
    {"order_id": "ZNY-2026-004", "email": "fraud_test@block.org", "currency": "USD", "amount_paid": 450.00, "item": "Bulk Order Alpha", "status": "FAILED"},
    {"order_id": "ZNY-2026-005", "email": "buyer3@lekki.ng", "currency": "NGN", "amount_paid": 127500.00, "item": "Signature Monogram Jalabiya", "status": "SUCCESS"}
]

def compile_ledger_analytics():
    """Parses multi-currency entries and normalizes financial balances into a target reporting base."""
    # Pull the exchange rate dynamically from the configuration asset layer
    config = load_system_config()
    if config:
        usd_to_ngn_rate = config["currency_rates"]["usd_to_ngn_peg"]
    else:
        usd_to_ngn_rate = 1500.00 # Safety hardcoded fallback parameter

    total_ngn_revenue = 0.0
    total_usd_revenue = 0.0
    successful_orders_count = 0
    failed_orders_count = 0
    item_breakdown = {}

    for order in MOCK_ORDER_LEDGER:
        if order["status"] == "FAILED":
            failed_orders_count += 1
            continue
            
        successful_orders_count += 1
        currency = order["currency"]
        amount = order["amount_paid"]
        item = order["item"]
        
        if currency == "NGN":
            total_ngn_revenue += amount
        elif currency == "USD":
            total_usd_revenue += amount
            
        item_breakdown[item] = item_breakdown.get(item, 0) + 1

    # Apply the runtime rate configuration value
    normalized_grand_total_ngn = total_ngn_revenue + (total_usd_revenue * usd_to_ngn_rate)

    print("============================================================")
    print("💰 ZANNIE BRAND E-COMMERCE GATEWAY FINANCIAL LEDGER MATRIX")
    print(f"Reporting Registry Rate: 1 USD = {usd_to_ngn_rate:,.2f} NGN")
    print("============================================================")
    print(f"📊 Transaction Volumes  : {successful_orders_count} Passed | {failed_orders_count} Dropped/Failed")
    print(f"💵 Native Cashflow (NGN): ₦{total_ngn_revenue:,.2f}")
    print(f"🇺🇸 Forex Cashflow (USD) : ${total_usd_revenue:,.2f}")
    print("------------------------------------------------------------")
    print(f"📈 COMBINED NET REVENUE  : ₦{normalized_grand_total_ngn:,.2f} NGN Equivalent")
    print("============================================================\n")

if __name__ == "__main__":
    compile_ledger_analytics()
