import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Device page URL (replace with an actual device page URL)
url = 'https://www.laptoparena.net/alienware/alienware-15-47xk2-grey-108277' 

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# Send a GET request
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    logging.info("Page fetched successfully")
except requests.RequestException as e:
    logging.error(f"Failed to fetch page: {e}")
    exit()

# Parse the page content
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the phone name
phone_name = soup.find('h1', class_='specs-phone-name-title').get_text(strip=True)

# Extract the main image URL
image_style = soup.select_one('.review-header .article-info style').get_text()
image_url = image_style.split("url(")[1].split(")")[0].strip()

# Extract specifications from the spotlight feature section
specs = {}
specs['Phone Name'] = phone_name
specs['Image URL'] = image_url

# Extract spotlight specs
spotlight_features = soup.select('.specs-spotlight-features li')
for feature in spotlight_features:
    key = feature.find('i').get('class')[1].replace('icon-', '').replace('-', ' ').title()
    value = feature.get_text(strip=True)
    specs[key] = value

# Extract detailed specs in each table
specs_tables = soup.select('#specs-list table')
for table in specs_tables:
    category = table.find('th').get_text(strip=True)  # E.g., Network, Display, Battery, etc.
    rows = table.select('tr')
    for row in rows:
        label = row.find('td', class_='ttl').get_text(strip=True)
        data = row.find('td', class_='nfo').get_text(strip=True)
        specs[f"{category} - {label}"] = data

# Print the specifications
print(f"Specifications for {phone_name}:")
print(f"Image URL: {image_url}\n")
for key, value in specs.items():
    print(f"{key}: {value}")
