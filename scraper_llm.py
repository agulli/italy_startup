import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import os
import json
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

# You will need to install google-genai: `pip install google-genai`
# And set your API key: `export GEMINI_API_KEY="your-api-key"`
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Ensure the API key is set
if not os.environ.get("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY environment variable not set. Please set it before running.")

client = genai.Client()

class StartupInfo(BaseModel):
    startup_name: str = Field(description="The name of the startup mentioned in the article.", default="N/A")
    location: str = Field(description="The city or country where the startup is based.", default="N/A")
    founders: str = Field(description="The names of the founders of the startup.", default="N/A")
    website: str = Field(description="The official website URL of the startup.", default="N/A")

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
            if re.search(r'eu-startups\.com/20\d{2}/\d{2}/', href):
                article_links.add(href)
        return list(article_links)
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return []

def extract_info_llm(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return None

    title = soup.title.text if soup.title else ""
    content = soup.find('div', class_='td-post-content')
    text = content.text if content else ""
    
    if not text:
        return None

    # Prompt Gemini to extract the information into a structured format
    prompt = f"Extract the startup name, location, founders, and website from the following article. Article Title: {title}\n\nArticle Text: {text}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StartupInfo,
                temperature=0.1,
            ),
        )
        
        # Parse the JSON response
        data = json.loads(response.text)
        
        return {
            'Startup Name': data.get('startup_name', 'N/A'),
            'Location': data.get('location', 'N/A'),
            'Founders': data.get('founders', 'N/A'),
            'Website': data.get('website', 'N/A'),
            'Article URL': url
        }
    except Exception as e:
        print(f"Error extracting data with Gemini for {url}: {e}")
        return {
            'Startup Name': 'Error',
            'Location': 'Error',
            'Founders': 'Error',
            'Website': 'Error',
            'Article URL': url
        }

def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Exiting: Please set your GEMINI_API_KEY environment variable.")
        return

    print("Fetching paginated article links...")
    all_links = set()
    
    # Just crawling 1 page for this example. Change range(1, 34) for all pages.
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(get_article_links, range(1, 34)))
    
    for result in results:
        for link in result:
            all_links.add(link)
            
    print(f"Total unique article links found: {len(all_links)}")
    print("Extracting info from articles using Gemini...")
    
    extracted_data = []
    # Since we are using an API, we should be mindful of rate limits.
    with ThreadPoolExecutor(max_workers=3) as executor:
        data = list(executor.map(extract_info_llm, all_links))
        
    for d in data:
        if d:
            extracted_data.append(d)
            
    print(f"Successfully extracted data from {len(extracted_data)} articles.")
    
    csv_file = 'italy_startups_llm.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Startup Name', 'Location', 'Founders', 'Website', 'Article URL'])
        writer.writeheader()
        writer.writerows(extracted_data)
        
    print(f"Data saved to {csv_file}")

if __name__ == "__main__":
    main()
