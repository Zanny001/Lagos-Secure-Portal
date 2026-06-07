import requests
import csv
import re
import time
from bs4 import BeautifulSoup
from random import randint
from config import DISCORD_WEBHOOK_URL

CSV_OUTPUT_PATH = "global_assistantships_leads.csv"
HIGH_VALUE_KEYWORDS = ["coordinator", "director", "chair", "admission", "grad", "fellowship"]

def init_csv():
    import os
    if not os.path.exists(CSV_OUTPUT_PATH):
        with open(CSV_OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Institution", "Department", "Faculty Name", "Title/Role", "Contact Email", "Profile Link"])

def dispatch_high_value_alert(institution, department, name, role, email, link):
    """Fires a Discord webhook when a high-value funding contact is identified."""
    payload = {
        "embeds": [{
            "title": "🎯 HIGH-VALUE ACADEMIC TARGET IDENTIFIED",
            "color": 5763719,
            "fields": [
                {"name": "Faculty Member", "value": f"**{name}**", "inline": True},
                {"name": "Title/Role", "value": f"`{role}`", "inline": True},
                {"name": "Institution Matrix", "value": f"*{institution} - {department}*", "inline": False},
                {"name": "Direct Contact", "value": f"📧 {email}", "inline": True},
                {"name": "Profile Reference", "value": f"[View Directory Profile]({link})", "inline": False}
            ],
            "footer": {"text": "Global Assistantship Harvester"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass

def save_academic_lead(data_tuple):
    with open(CSV_OUTPUT_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data_tuple)
    print(f"🎓 [SAVED] {data_tuple[2]} | {data_tuple[4]}")
    
    # Check if the role triggers an alert
    role_lower = data_tuple[3].lower()
    if any(keyword in role_lower for keyword in HIGH_VALUE_KEYWORDS):
        dispatch_high_value_alert(*data_tuple)

def scrape_university_directory(institution_name, start_url, department_name):
    print(f"\n[SCANNING] Initializing academic sweep -> {institution_name} ({department_name})")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(start_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[WARNING] Directory offline or blocked: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        profiles = soup.find_all(['div', 'li', 'tr'], class_=re.compile(r'(?:faculty|staff|profile|person|member)', re.I))
        
        if not profiles:
            print(f"[-] No standard profile blocks found at {start_url}.")
            return
            
        for profile in profiles:
            name_tag = profile.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'(?:name|title)', re.I))
            if not name_tag: continue
            faculty_name = name_tag.get_text(strip=True)
            
            role_tag = profile.find(['span', 'p', 'div'], class_=re.compile(r'(?:title|role|position)', re.I))
            role = role_tag.get_text(strip=True) if role_tag else "Faculty Member"
            
            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', profile.get_text(" "))
            email = email_match.group(0) if email_match else "N/A"
            
            link_tag = profile.find('a', href=True)
            profile_link = link_tag['href'] if link_tag else start_url
            if profile_link.startswith('/'):
                from urllib.parse import urlparse
                parsed_uri = urlparse(start_url)
                profile_link = f"{parsed_uri.scheme}://{parsed_uri.netloc}{profile_link}"
                
            if email != "N/A":
                save_academic_lead((institution_name, department_name, faculty_name, role, email, profile_link))
                
    except Exception as e:
        print(f"[ERROR] Sweep exception: {e}")

if __name__ == "__main__":
    init_csv()
    academic_targets = [
        {"institution": "Demo University", "department": "Computer Science", "url": "https://example.edu/cs/faculty"}
    ]
    for target in academic_targets:
        scrape_university_directory(target["institution"], target["url"], target["department"])
        time.sleep(randint(2, 6))
