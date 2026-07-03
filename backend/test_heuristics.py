import requests
from bs4 import BeautifulSoup
import re
import csv
import time

def extract_info(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return None

    title = soup.title.text if soup.title else ""
    
    # Heuristic for name: usually in the title
    name = "N/A"
    # Example title: "AI for the workers it can’t replace: Italy’s Gyver raises €1.4 million to empower electricians | EU-Startups"
    # Or "Milan-based Fiscozen raises €8 million..."
    if " raises " in title:
        parts = title.split(" raises ")[0].split()
        name = parts[-1]
        if name.endswith("s") and "'" in name: # e.g. Italy's
            name = name
    elif " secures " in title:
        parts = title.split(" secures ")[0].split()
        name = parts[-1]
    
    # Let's clean the name a bit
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    
    content = soup.find('div', class_='td-post-content')
    location = "N/A"
    founders = "N/A"
    website = "N/A"
    
    if content:
        text = content.text
        
        # Location heuristic
        loc_match = re.search(r'([A-Z][a-zA-Z\s,]+)-based', text)
        if loc_match:
            location = loc_match.group(1).strip()
            
        # Founders heuristic
        # "founded ... by X, Y and Z" or "co-founder X"
        founder_match = re.search(r'founded .*? by ([A-Z][a-zA-Z\s,and]+?)\.', text, re.IGNORECASE)
        if founder_match:
            founders = founder_match.group(1).strip()
        else:
            founder_match = re.search(r'([A-Z][a-zA-Z\s]+), co-founder', text)
            if founder_match:
                founders = founder_match.group(1).strip()

        # Website heuristic
        links = content.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'eu-startups.com' not in href and 'twitter.com' not in href and 'linkedin.com' not in href and 'facebook.com' not in href:
                website = href
                break # usually the startup website is one of the first external links, or we could look for it
                
    return {
        'Startup Name': name,
        'Location': location,
        'Founders': founders,
        'Website': website,
        'Article URL': url
    }

urls = [
    'https://www.eu-startups.com/2026/05/ai-for-the-workers-it-cant-replace-italys-gyver-raises-e1-4-million-to-empower-electricians/',
    'https://www.eu-startups.com/2026/06/bolzano-based-soource-raises-e3-million-to-help-procurement-evolve-from-copilot-to-autopilot-model/',
    'https://www.eu-startups.com/2026/05/quantum-software-startup-algorithmiq-raises-e18-million-and-moves-global-hq-from-helsinki-to-milan/',
    'https://www.eu-startups.com/2026/05/italian-ai-company-webidoo-secures-e21-million-to-scale-smb-focused-automation-platform/'
]

for u in urls:
    print(extract_info(u))
