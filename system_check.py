import http.client
import json
import os
import subprocess
import sys

# Color configurations for clear terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

LOCAL_HOST = "127.0.0.1"
PORT = 5005

def check_local_endpoint(path):
    """Pings an internal server endpoint path and evaluates its response status."""
    try:
        conn = http.client.HTTPConnection(LOCAL_HOST, PORT, timeout=3)
        conn.request("GET", path)
        response = conn.getresponse()
        status = response.status
        data = response.read().decode('utf-8')
        conn.close()
        return status, data
    except Exception:
        return None, None

def inspect_active_processes():
    """Scans the system process tree to see if the core Flask API engine is running."""
    try:
        # Runs a standard ps command to look for your API script instance
        output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
        if "realestate_api.py" in output:
            return True
        return False
    except Exception:
        return False

def run_system_diagnostic():
    """Executes a full diagnostic evaluation of your backend infrastructure nodes."""
    print(f"\n{BOLD}=== ZANNIE HUB SYSTEM HEALTH DIAGNOSTIC ==={RESET}\n")
    
    # 1. Process Level Check
    print("[*] Auditing running background services...")
    api_process_active = inspect_active_processes()
    if api_process_active:
        print(f"    -> Flask API Process Status: {GREEN}RUNNING{RESET}")
    else:
        print(f"    -> Flask API Process Status: {RED}OFFLINE (CRITICAL){RESET}")

    # 2. Network Port Level Check
    print("\n[*] Auditing internal port bindings (Port 5005)...")
    root_status, root_data = check_local_endpoint("/")
    
    if root_status == 200:
        print(f"    -> Local Server Port Link: {GREEN}ONLINE & RESPONSIVE{RESET}")
        try:
            parsed_info = json.loads(root_data)
            print(f"    -> Node Owner/Operator: {BOLD}{parsed_info.get('node_owner')}{RESET}")
        except Exception:
            pass
    else:
        print(f"    -> Local Server Port Link: {RED}UNREACHABLE{RESET}")

    # 3. Dedicated Route API Checks
    print("\n[*] Validating database route telemetry channels...")
    
    # Check Real Estate Scraper Data Route
    re_status, _ = check_local_endpoint("/api/metrics")
    if re_status == 200:
        print(f"    -> /api/metrics (Real Estate Node): {GREEN}OK (200){RESET}")
    else:
        print(f"    -> /api/metrics (Real Estate Node): {RED}ERROR/OFFLINE{RESET}")
        
    # Check Academic Performance Data Route
    ac_status, _ = check_local_endpoint("/api/students")
    if ac_status == 200:
        print(f"    -> /api/students (Academic Node)   : {GREEN}OK (200){RESET}")
    else:
        print(f"    -> /api/students (Academic Node)   : {RED}ERROR/OFFLINE{RESET}")

    # 4. Summary & Action Plan Evaluation
    print(f"\n{BOLD}=== DIAGNOSTIC REPORT SUMMARY ==={RESET}")
    if api_process_active and root_status == 200 and re_status == 200 and ac_status == 200:
        print(f"{GREEN}{BOLD}[SUCCESS] All localized platform nodes and pipeline endpoints are functioning perfectly.{RESET}\n")
        sys.exit(0)
    else:
        print(f"{YELLOW}{BOLD}[WARNING] Infrastructure degradation detected. Check process logs or restart realestate_api.py.{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    run_system_diagnostic()

