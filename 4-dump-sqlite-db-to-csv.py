import sqlite3
from openpyxl import Workbook

# Database path
results_db_path = r'C:\Users\Ymir\Desktop\Git Adventure\Github-7NOV24\gsmarena\steps\data\results.db'

# Connect to results.db
conn = sqlite3.connect(results_db_path)
cursor = conn.cursor()

# Fetch all data from the device_specs table
cursor.execute("SELECT * FROM device_specs")
rows = cursor.fetchall()

# Get column names for the Excel header
column_names = [description[0] for description in cursor.description]

# Specify the output Excel file path
excel_file_path = r'C:\Users\Ymir\Desktop\Git Adventure\Github-7NOV24\gsmarena\steps\data\device_specs.xlsx'

# Create a new workbook and add a sheet
workbook = Workbook()
sheet = workbook.active
sheet.title = "Device Specs"

# Write the header row
sheet.append(column_names)

# Write data rows
for row in rows:
    sheet.append(row)

# Save the workbook to the specified Excel file
workbook.save(excel_file_path)

# Close the database connection
conn.close()

print(f"Data successfully exported to {excel_file_path}")
