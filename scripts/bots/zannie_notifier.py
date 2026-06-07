import time
import os

def dispatch_order_notifications(order_id, customer_email, amount_kobo):
    """
    Triggers automated downstream fulfillment tasks once payment is verified.
    Forces absolute paths and flushes file write streams immediately.
    """
    amount_ngn = amount_kobo / 100
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Structure the dispatch message
    alert_log = (
        f"\n==================================================\n"
        f"[DISPATCH EVENT] {timestamp}\n"
        f"Order ID:        {order_id}\n"
        f"Customer Email:  {customer_email}\n"
        f"Amount Fulfilled: ₦{amount_ngn:,.2f}\n"
        f"Status:          DIGITAL_ASSETS_DISPATCHED\n"
        f"Action:          Sending confirmation email link to client...\n"
        f"==================================================\n"
    )
    
    # 2. Force an absolute path to ensure it lands right in your workspace directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(current_dir, "fulfillment_dispatch.log")
    
    # 3. Append the event and explicitly call flush() and os.fsync() to force the disk write
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(alert_log)
            f.flush()  # Force internal buffers out to the OS
            os.fsync(f.fileno())  # Force the OS to write to physical storage
        print(f"[NOTIFIER SUCCESS] Absolute file write completed at: {log_path}")
        return True
    except Exception as e:
        print(f"[NOTIFIER FAULT] Failed to write file: {e}")
        return False

