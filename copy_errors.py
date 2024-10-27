import pandas as pd
import shutil
import os

# Read the CSV file
csv_path = 'errors_local.csv'  # Replace with the path to your CSV file
df = pd.read_csv(csv_path)

# Define source and destination directories
source_dir = '/Volumes/TOSHIBA/Rekordbox_database'
destination_dir = '/Volumes/TOSHIBA/Rekordbox_database_selected'

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    original_path = row['Path']
    
    # Extract the filename from the path
    filename = os.path.basename(original_path)
    
    # Define the source and destination file paths
    source_path = os.path.join(source_dir, filename)
    destination_path = os.path.join(destination_dir, filename)
    
    # Check if the source file exists before attempting to copy
    if os.path.isfile(source_path):
        try:
            shutil.copy2(source_path, destination_path)
            print(f"Copied: {source_path} to {destination_path}")
        except Exception as e:
            print(f"Failed to copy {source_path}: {e}")
    else:
        print(f"File does not exist: {source_path}")
