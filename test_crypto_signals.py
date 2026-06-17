import time

# Simulation variables
mock_cache = {"BTC": 65000.0}
VOLATILITY_THRESHOLD = 2.0

def simulate_market_check(simulated_new_price):
    """
    Simulates a single price-checking iteration against the cached baseline.
    """
    last_price = mock_cache["BTC"]
    percent_change = ((simulated_new_price - last_price) / last_price) * 100
    
    print(f"\n[SCAN] Old Price: ${last_price:,.2f} | New Price: ${simulated_new_price:,.2f}")
    print(f"[MATH] Calculated Movement: {percent_change:+.2f}%")
    
    if abs(percent_change) >= VOLATILITY_THRESHOLD:
        print(f"🎯 [TRIGGER] Volatility threshold crossed! Dispatching Discord Alert card.")
        # Update cache baseline upon trigger
        mock_cache["BTC"] = simulated_new_price
    else:
        print("💤 [IGNORE] Movement stable. No alert sent to Discord channel.")

if __name__ == "__main__":
    print("=== INITIALIZING CRYPTO ENGINE SIMULATION ===")
    print(f"Starting baseline: BTC/USD = ${mock_cache['BTC']:,.2f}")
    print(f"Target Alert Threshold: ±{VOLATILITY_THRESHOLD}%")
    
    # Iteration 1: Simulate stable market noise (0.3% increase)
    time.sleep(1)
    simulate_market_check(65195.0)
    
    # Iteration 2: Simulate a sudden market spike (5.07% increase from the original baseline)
    time.sleep(1)
    simulate_market_check(68500.0)
    
    # Iteration 3: Simulate another stable period relative to the updated baseline (0.15% drop)
    time.sleep(1)
    simulate_market_check(68400.0)
    
    print("\n=== SIMULATION CYCLE COMPLETE ===")

