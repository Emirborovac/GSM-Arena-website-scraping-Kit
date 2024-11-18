
# GSM Arena Phone Specs Scraper - README

## Overview

This repository contains a series of Python scripts designed to scrape phone specifications from the GSM Arena website. The scripts are structured to extract data in a multi-step process, starting from brand categories and ending with detailed phone specifications. The final data can be exported to a CSV or Excel file for further use.

---

## Prerequisites

- Python 3.8 or higher
- Required libraries: 
  - `requests`
  - `beautifulsoup4`
  - `sqlite3` (built-in)
  - `openpyxl` (for exporting to Excel)
  - `logging`

Install missing libraries with:
```bash
pip install requests beautifulsoup4 openpyxl
```

---

## Script Descriptions

### 1. `1-extract-categories-URLs.py`

- **Purpose**: Scrapes phone brand categories and URLs from GSM Arena and saves them into an SQLite database (`phone_categories.db`).
- **Database Table**: `categories`
  - `id`: Auto-increment ID.
  - `name`: Brand name.
  - `url`: URL of the brand page.

---

### 2. `2-extract-device-model-URLs.py`

- **Purpose**: Extracts device model names and URLs for each brand category and stores them in an SQLite database (`devices.db`).
- **Database Table**: `devices`
  - `id`: Auto-increment ID.
  - `brand_name`: Name of the brand.
  - `device_model`: Model name of the device.
  - `device_url`: URL of the device page.

---

### 3. `3-extract-device-specs.py`

- **Purpose**: Scrapes detailed specifications for a single device and prints them to the console. This script is intended for testing individual URLs.
- **Data Extracted**:
  - Phone name.
  - Main image URL.
  - Spotlight specifications.
  - Detailed technical specifications.

---

### 4. `4-dump-sqlite-db-to-csv.py`

- **Purpose**: Exports data from the SQLite database (`results.db`) to an Excel file (`device_specs.xlsx`).
- **Steps**:
  - Connects to the `device_specs` table.
  - Writes the data to an Excel file.

---

### 5. `5-ultimate-specs-script.py`

- **Purpose**: Combines all steps to scrape detailed specifications for all devices, leveraging proxies to handle multiple requests and avoid bans.
- **Database Table**: `device_specs` in `results.db`
  - Columns dynamically created based on extracted specifications.
  - Example columns: `brand_name`, `device_name`, `image_url`, and other spec fields.

---

## Execution Steps

1. Run `1-extract-categories-URLs.py` to scrape brand categories.
2. Run `2-extract-device-model-URLs.py` to scrape device models for each brand.
3. (Optional) Run `3-extract-device-specs.py` to test scraping for a single device.
4. Run `5-ultimate-specs-script.py` to scrape all device specifications and save them to the database.
5. Run `4-dump-sqlite-db-to-csv.py` to export the final data to an Excel file.

---

## Notes

- **Proxy Setup**: The `5-ultimate-specs-script.py` uses a rotating proxy setup. Update the `username`, `password`, and `proxy_base` in the script before running.
- **Database Path**: Ensure the database paths in the scripts are updated to your local environment.

---

## Output

- SQLite databases:
  - `phone_categories.db`: Stores brand categories.
  - `devices.db`: Stores device model information.
  - `results.db`: Stores detailed specifications.
- Excel file:
  - `device_specs.xlsx`: Final export of all scraped data.
