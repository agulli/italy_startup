import requests
from bs4 import BeautifulSoup
import re
import csv
import time
from concurrent.futures import ThreadPoolExecutor

def get_article_links(page_num):
    url = f'https://www.eu-startups.com/category/italy-startups/page/{page_num}/' if page_num > 1 else 'https://www.eu-startups.com/category/italy-startups/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)
        article_links = set()
        for link in links:
            href = link['href']
            # Basic check to see if it's an article (contains a year and a month usually)
            if re.search(r'eu-startups\.com/20\d{2}/\d{2}/', href):
                article_links.add(href)
        return list(article_links)
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return []

def extract_info(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return None

    title = soup.title.text if soup.title else ""
    
    name = "N/A"
    if " raises " in title:
        parts = title.split(" raises ")[0].split()
        name = parts[-1]
        if name.endswith("s") and "'" in name:
            name = name
    elif " secures " in title:
        parts = title.split(" secures ")[0].split()
        name = parts[-1]
    elif " acquires " in title:
        parts = title.split(" acquires ")[0].split()
        name = parts[-1]
    else:
        # Fallback to the word before "-based" or a similar heuristic
        pass
        
    name = re.sub(r'[^a-zA-Z0-9\-\']', '', name)
    if name == "": name = "N/A"
    
    content = soup.find('div', class_='td-post-content')
    location = "N/A"
    founders = "N/A"
    website = "N/A"
    
    if content:
        text = content.text
        
        loc_match = re.search(r'([A-Z][a-zA-Z\s,]+)-based', text)
        if loc_match:
            location = loc_match.group(1).strip()
            
        founder_match = re.search(r'founded .*? by ([A-Z][a-zA-Z\s,and]+?)\.', text, re.IGNORECASE)
        if founder_match:
            founders = founder_match.group(1).strip()
        else:
            founder_match = re.search(r'([A-Z][a-zA-Z\s]+), co-founder', text)
            if founder_match:
                founders = founder_match.group(1).strip()

        links = content.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'eu-startups.com' not in href and 'twitter.com' not in href and 'linkedin.com' not in href and 'facebook.com' not in href and 'instagram.com' not in href and 'mailto:' not in href:
                website = href
                break
                
    return {
        'Startup Name': name,
        'Location': location,
        'Founders': founders,
        'Website': website,
        'Article URL': url
    }

def main():
    print("Fetching paginated article links...")
    all_links = set()
    
    # Based on our previous check, there are 33 pages.
    # Let's crawl pages 1 to 33.
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(get_article_links, range(1, 34)))
    
    for result in results:
        for link in result:
            all_links.add(link)
            
    print(f"Total unique article links found: {len(all_links)}")
    print("Extracting info from articles...")
    
    extracted_data = []
    # To be polite and not overwhelm the server too much, we use a slightly larger pool for fetching articles
    with ThreadPoolExecutor(max_workers=10) as executor:
        data = list(executor.map(extract_info, all_links))
        
    for d in data:
        if d:
            extracted_data.append(d)
            
    print(f"Successfully extracted data from {len(extracted_data)} articles.")
    
    csv_file = 'italy_startups.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Startup Name', 'Location', 'Founders', 'Website', 'Article URL'])
        writer.writeheader()
        writer.writerows(extracted_data)
        
    print(f"Data saved to {csv_file}")

if __name__ == "__main__":
    main()
