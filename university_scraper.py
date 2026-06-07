import requests
import csv
import re
import time
from bs4 import BeautifulSoup
from random import randint

CSV_OUTPUT_PATH = "global_assistantships_leads.csv"

def init_csv():
    """Initializes the output file with the correct headers."""
    with open(CSV_OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Institution", "Department", "Faculty Name", "Title/Role", "Contact Email", "Profile Link"])

def save_academic_lead(data_tuple):
    """Appends a successfully parsed faculty lead to the CSV."""
    with open(CSV_OUTPUT_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data_tuple)
    print(f"🎓 [SAVED] {data_tuple[2]} | {data_tuple[4]}")

def scrape_university_directory(institution_name, start_url, department_name):
    """
    Crawls a target academic directory. 
    (Note: HTML structures vary wildly by university; this uses a generalized approach targeting standard faculty cards).
    """
    print(f"\n[SCANNING] Initializing academic sweep -> {institution_name} ({department_name})")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(start_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[WARNING] Directory offline or blocked: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # General targeting for faculty/staff lists (adjust classes based on specific university sites)
        profiles = soup.find_all(['div', 'li', 'tr'], class_=re.compile(r'(?:faculty|staff|profile|person|member)', re.I))
        
        if not profiles:
            print(f"[-] No standard profile blocks found at {start_url}. Custom HTML parsing rules may be required.")
            return
            
        for profile in profiles:
            # Extract Name
            name_tag = profile.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'(?:name|title)', re.I))
            if not name_tag:
                continue
            faculty_name = name_tag.get_text(strip=True)
            
            # Extract Role/Title (e.g., Professor, Graduate Coordinator)
            role_tag = profile.find(['span', 'p', 'div'], class_=re.compile(r'(?:title|role|position)', re.I))
            role = role_tag.get_text(strip=True) if role_tag else "Faculty Member"
            
            # Extract Email using a strict regex across the profile text
            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', profile.get_text(" "))
            email = email_match.group(0) if email_match else "N/A"
            
            # Extract Profile Link
            link_tag = profile.find('a', href=True)
            profile_link = link_tag['href'] if link_tag else start_url
            if profile_link.startswith('/'):
                from urllib.parse import urlparse
                parsed_uri = urlparse(start_url)
                base_url = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                profile_link = base_url + profile_link
                
            if email != "N/A":
                save_academic_lead((institution_name, department_name, faculty_name, role, email, profile_link))
                
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network exception during sweep: {e}")

if __name__ == "__main__":
    print("=====================================================")
    print("   GLOBAL ACADEMIC HARVESTER: FUNDING PIPELINE ONLINE  ")
    print("=====================================================")
    init_csv()
    
    # Example Target Matrix - Swap these out for actual program URLs
    academic_targets = [
        {
            "institution": "Mock University (Demo)", 
            "department": "Physics & Astronomy", 
            "url": "https://example.edu/physics/faculty"
        }
    ]
    
    for target in academic_targets:
        scrape_university_directory(target["institution"], target["url"], target["department"])
        time.sleep(randint(2, 6))
        
    print("\n[COMPLETE] Academic sweep finished. Check global_assistantships_leads.csv")
