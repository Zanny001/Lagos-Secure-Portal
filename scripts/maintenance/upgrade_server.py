import os
import subprocess
import sys

TARGET_FILE = "realestate_api.py"

UPGRADE_CODE = """
@app.route('/api/syllabus', methods=['GET'])
def get_syllabus_manifest():
    try:
        with open('lessons_manifest.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        response = jsonify(data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
    except Exception as e:
        response = jsonify({"status": "error", "message": str(e)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500
"""

def patch_and_restart():
    print("\\n\\033[1m[*] Initiating Live Backend Server Upgrade...\\033[0m")
    
    if not os.path.exists(TARGET_FILE):
        print(f"[-] Target file '{TARGET_FILE}' not found in current directory.")
        sys.exit(1)
        
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # Avoid injecting the route twice if script is re-run
    if "/api/syllabus" in content:
        print("[*] Target endpoint route already injected into script architecture.")
    else:
        # Inject right before the standard driver initialization block
        if "__main__" in content:
            content = content.replace("if __name__ == '__main__':", f"{UPGRADE_CODE}\nif __name__ == '__main__':")
            with open(TARGET_FILE, "w") as f:
                f.write(content)
            print("[+] Successfully injected /api/syllabus endpoint route mapping.")
        else:
            print("[-] Critical Error: Could not locate standard __main__ boot frame.")
            sys.exit(1)

    # 2. Terminate the old background task instance cleanly
    print("[*] Sweeping old process tree allocations...")
    try:
        pids = subprocess.check_output(["pgrep", "-f", TARGET_FILE]).decode().split()
        for pid in pids:
            if int(pid) != os.getpid():
                subprocess.run(["kill", "-9", pid])
                print(f"    -> Terminated active zombie process allocation ID: {pid}")
    except Exception:
        print("    -> No existing background instances found running.")

    # 3. Relaunch server task inside a background daemon context
    print("[*] Relaunching upgraded multi-database Flask backend...")
    subprocess.Popen(
        ["nohup", "python3", TARGET_FILE],
        stdout=open(os.devnull, "w"),
        stderr=open(os.devnull, "w"),
        preexec_fn=os.setpgrp
    )
    print("\\033[92m\\033[1m[SUCCESS] Upgraded server running smoothly in the background on Port 5005!\\033[0m\\n")

if __name__ == "__main__":
    patch_and_restart()

