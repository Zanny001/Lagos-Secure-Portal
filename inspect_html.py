from bs4 import BeautifulSoup

print("[*] Analyzing saved HTML structure...")
with open('debug_live_page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Look for standard heading tags which usually hold property titles
headings = soup.find_all(['h2', 'h3', 'h4'])

for h in headings:
    text = h.get_text().lower()
    # If the heading mentions bedrooms, duplex, etc., it's a property card!
    if 'bedroom' in text or 'duplex' in text or 'apartment' in text or 'sale' in text:
        # Get the main container holding this title
        parent_card = h.find_parent('div')
        
        print("\n========================================")
        print(f"FOUND LIKELY PROPERTY CONTAINER")
        print(f"Class Name: {parent_card.get('class')}")
        print("========================================")
        
        # Print the first 800 characters of this container's HTML structure
        print(parent_card.prettify()[:800])
        print("\n========================================")
        break
else:
    print("[-] Could not automatically identify a property card. The site might be using JavaScript rendering.")
