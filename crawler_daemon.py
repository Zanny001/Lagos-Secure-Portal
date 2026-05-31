import os
import sys
import time
import subprocess
from datetime import datetime

# Configuration parameters
INTERVAL_SECONDS = 1800  # 30 Minutes loop cycle
CRAWLER_SCRIPT = "realestate_crawler.py"
LOG_FILE = "daemon_harvest.log"

def log_message(message):
    """Writes a timestamped entry to the local daemon execution log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(log_entry)

def run_harvester_cycle():
    """Executes the real estate crawler script as an independent subprocess."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, CRAWLER_SCRIPT)
    
    if not os.path.exists(script_path):
        log_message(f"[CRITICAL ERROR] Target script '{CRAWLER_SCRIPT}' not found at {script_path}")
        return False

    log_message(f"[*] Starting background execution cycle for {CRAWLER_SCRIPT}...")
    
    try:
        # Run the crawler and capture output states
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        log_message(f"[SUCCESS] Crawler cycle completed cleanly.")
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"[ERROR] Crawler runtime crash. Exit code: {e.returncode}")
        if e.stderr:
            log_message(f"[ERROR DETAILED] {e.stderr.strip()}")
        return False
    except Exception as e:
        log_message(f"[ERROR] Subprocess pipeline failure: {str(e)}")
        return False

def main():
    log_message("==================================================")
    log_message("🚀 ZANNIE REAL ESTATE CRAWLER DAEMON INITIALIZED ")
    log_message(f"[*] Persistent interval established: Every {INTERVAL_SECONDS // 60} minutes.")
    log_message("==================================================")
    
    # Run an immediate initial harvest upon launch to verify link integration
    run_harvester_cycle()
    
    try:
        while True:
            log_message(f"[ZzZ] Standing by for next cycle interval...")
            time.sleep(INTERVAL_SECONDS)
            run_harvester_cycle()
    except KeyboardInterrupt:
        log_message("[!] Daemon shutdown sequence requested by user. Exiting cleanly.")
    except Exception as e:
        log_message(f"[CRITICAL BREAK] Daemon loop failed globally: {str(e)}")

if __name__ == "__main__":
    main()

