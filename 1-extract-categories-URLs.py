import requests
from bs4 import BeautifulSoup
import logging
import sqlite3
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL of the page to scrape
url = 'https://www.gsmarena.com/makers.php3'
base_url = 'https://www.gsmarena.com/'  # Base URL to form full links

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# Connect to SQLite database (or create it)
conn = sqlite3.connect('phone_categories.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL
    )
''')
conn.commit()

# Send a GET request to the page with headers
try:
    logging.info(f"Sending request to {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure the request was successful
    logging.info("Request successful")
except requests.exceptions.RequestException as e:
    logging.error(f"Error during requests to {url} : {str(e)}")
    exit()

# Parse the page content
soup = BeautifulSoup(response.text, 'html.parser')

# Select the <td> elements within the .st-text div
cells = soup.select('.st-text td')

# Check if any cells were found
if not cells:
    logging.warning("No cells found with the specified selector")

# Loop through each cell to get the link and the brand information
for cell in cells:
    link = cell.find('a')
    if link:
        href = link.get('href')
        full_url = base_url + href  # Form the full URL
        name = link.get_text(separator=" ", strip=True)  # Extract full text

        # Use regex to remove any numbers and the word "devices" from the name
        brand_name = re.sub(r'\s*\d+\s*devices', '', name)  # Removes "100 devices", "47 devices", etc.

        # Insert brand name and URL into the database
        cursor.execute('INSERT INTO categories (name, url) VALUES (?, ?)', (brand_name, full_url))
        conn.commit()  # Commit after each insert for safety

        print(f"Inserted into database: {brand_name} - {full_url}")
    else:
        logging.warning("No link found in this cell")

# Close the database connection
conn.close()
