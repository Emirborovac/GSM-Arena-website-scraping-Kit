import requests
from bs4 import BeautifulSoup
import logging
import sqlite3
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database paths
devices_db_path = r'C:\Users\Ymir\Desktop\Git Adventure\Github-7NOV24\gsmarena\steps\data\devices.db'
results_db_path = r'C:\Users\Ymir\Desktop\Git Adventure\Github-7NOV24\gsmarena\steps\data\results.db'

# Working proxy setup
username = ''
password = ''
proxy_base = 'dc.oxylabs.io'
current_port = 8050
max_port = 8060

proxies = {
    "https": f"https://user-{username}:{password}@{proxy_base}:{current_port}",
    "http": f"http://user-{username}:{password}@{proxy_base}:{current_port}"
}

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# Connect to devices.db to fetch device URLs
conn_devices = sqlite3.connect(devices_db_path)
cursor_devices = conn_devices.cursor()

# Connect to results.db (create if it doesn't exist)
conn_results = sqlite3.connect(results_db_path)
cursor_results = conn_results.cursor()

# Create the initial table in results.db
cursor_results.execute('''
    CREATE TABLE IF NOT EXISTS device_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_name TEXT,
        device_name TEXT,
        image_url TEXT
    )
''')
conn_results.commit()

# Function to add a new column if it doesn't already exist
def add_column_if_not_exists(column_name):
    try:
        cursor_results.execute(f"ALTER TABLE device_specs ADD COLUMN '{column_name}' TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

# Fetch all device URLs from devices.db
cursor_devices.execute("SELECT brand_name, device_model, device_url FROM devices")
devices = cursor_devices.fetchall()

# Function to fetch and parse device specifications with port rotation
def fetch_device_specs(url):
    global current_port
    while True:
        try:
            # Update the proxy port before each request
            proxies["https"] = f"https://user-{username}:{password}@{proxy_base}:{current_port}"
            proxies["http"] = f"http://user-{username}:{password}@{proxy_base}:{current_port}"
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            logging.info(f"Page fetched successfully from {url}")
            break  # Exit loop if successful

        except requests.RequestException as e:
            logging.error(f"Request failed on port {current_port}: {e}")
            current_port += 1  # Increment the port number
            if current_port > max_port:
                current_port = 8050  # Reset to starting port if max exceeded

            logging.info(f"Switching to next port: {current_port}")

    soup = BeautifulSoup(response.text, 'html.parser')
    specs = {}

    # Extract phone name and image URL
    phone_name = soup.find('h1', class_='specs-phone-name-title').get_text(strip=True)
    image_style = soup.select_one('.review-header .article-info style')
    image_url = image_style.get_text().split("url(")[1].split(")")[0].strip() if image_style else None

    specs['device_name'] = phone_name
    specs['image_url'] = image_url

    # Extract detailed specs
    specs_tables = soup.select('#specs-list table')
    for table in specs_tables:
        category = table.find('th').get_text(strip=True).lower()
        rows = table.select('tr')
        for row in rows:
            label_td = row.find('td', class_='ttl')
            data_td = row.find('td', class_='nfo')
            
            if label_td and data_td:
                subfield = label_td.get_text(strip=True)
                data = data_td.get_text(strip=True)
                
                # Create column name with category and subfield
                column_name = f"{category} - {subfield}"
                add_column_if_not_exists(column_name)  # Add column if it doesn't exist
                specs[column_name] = data

    return specs

# Populate the results.db with each device's specs
for brand_name, device_name, device_url in devices:
    logging.info(f"Fetching specs for {brand_name} - {device_name}")
    specs = fetch_device_specs(device_url)
    if specs:
        # Ensure brand_name and device_name are added to specs
        specs['brand_name'] = brand_name
        specs['device_name'] = device_name

        # Insert data into results.db
        columns = ', '.join(f'"{key}"' for key in specs.keys())
        placeholders = ', '.join('?' for _ in specs)
        values = list(specs.values())
        
        cursor_results.execute(f"INSERT INTO device_specs ({columns}) VALUES ({placeholders})", values)
        conn_results.commit()
        
        logging.info(f"Inserted {brand_name} - {device_name} into results.db")
    
    # Optional sleep to avoid overwhelming the server
    time.sleep(1)

# Close database connections
conn_devices.close()
conn_results.close()
