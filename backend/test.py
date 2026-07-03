import requests
from bs4 import BeautifulSoup

url = 'https://www.eu-startups.com/category/italy-startups/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

pagination = soup.find('div', class_='page-nav')
if pagination:
    last_page_link = pagination.find('a', class_='last')
    if last_page_link:
        print(f"Last page: {last_page_link.text}")
    else:
        # get all page numbers
        pages = pagination.find_all('a')
        for page in pages:
            print(page.text)
else:
    print("No pagination found")
