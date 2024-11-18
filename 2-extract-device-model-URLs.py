import requests
from bs4 import BeautifulSoup
import logging
import sqlite3
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL
base_url = 'https://www.gsmarena.com/'

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# Connect to phone_categories.db to get category URLs
category_db_path = r'C:\Users\Ymir\Desktop\Git Adventure\Github-7NOV24\gsmarena\steps\data\phone_categories.db'
conn_categories = sqlite3.connect(category_db_path)
cursor_categories = conn_categories.cursor()

# Connect to devices.db (create if it doesn't exist)
devices_db_path = r'C:\Users\Ymir\Desktop\Git Adventure\Github-7NOV24\gsmarena\steps\data\devices.db'
conn_devices = sqlite3.connect(devices_db_path)
cursor_devices = conn_devices.cursor()

# Create table in devices.db if it doesn't exist
cursor_devices.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_name TEXT NOT NULL,
        device_model TEXT NOT NULL,
        device_url TEXT NOT NULL
    )
''')
conn_devices.commit()

def get_device_links(page_url, brand_name):
    """
    Extracts and stores device links and model names for a given brand category page.
    Returns the URL of the next page if it exists, otherwise None.
    """
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch page {page_url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Select device links in the .makers div
    device_links = soup.select('.makers li a')
    for link in device_links:
        href = link.get('href')
        full_url = base_url + href
        device_model = link.select_one('span').text.strip()  # Extract device model name

        # Insert device data into devices.db
        cursor_devices.execute(
            'INSERT INTO devices (brand_name, device_model, device_url) VALUES (?, ?, ?)',
            (brand_name, device_model, full_url)
        )
        conn_devices.commit()
        logging.info(f"Inserted device: {brand_name} - {device_model} - {full_url}")

    # Check if there is a "Next" button for pagination
    next_button = soup.select_one('.nav-pages a[class="prevnextbutton"][title="Next page"]')
    if next_button:
        next_url = base_url + next_button.get('href')
        return next_url
    else:
        return None

# Fetch all brand categories from phone_categories.db
cursor_categories.execute("SELECT name, url FROM categories")
categories = cursor_categories.fetchall()

# Iterate over each brand category
for brand_name, category_url in categories:
    logging.info(f"Starting scrape for brand: {brand_name} - URL: {category_url}")

    # Scrape all device links for the current brand, following pagination
    current_url = category_url
    while current_url:
        logging.info(f"Scraping page: {current_url}")
        current_url = get_device_links(current_url, brand_name)
        time.sleep(1)  # Optional delay to avoid overwhelming the server

# Close database connections
conn_categories.close()
conn_devices.close()
