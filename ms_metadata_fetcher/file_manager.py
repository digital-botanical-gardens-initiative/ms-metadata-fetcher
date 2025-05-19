import csv
import os
import shutil
from datetime import datetime

import requests
from dotenv import load_dotenv

# Loads .env variables
load_dotenv()

# Define file paths and folder paths
tsv_file_path = "metadata.tsv"
source_folder = str(os.getenv("SOURCE_FOLDER"))
destination_path = str(os.getenv("DESTINATION_FOLDER"))
date = datetime.now().strftime("%Y%m%d%H")
subset_path = f"subset_{date}"
suffix = ".tsv"
metadata_path = f"metadata_{date}{suffix}"
destination_folder = os.path.join(destination_path, subset_path)
destination_metadata = os.path.join(destination_path, metadata_path)
column_name = "ms_filename"  # Replace with the actual column name

directus_email = os.getenv("DIRECTUS_EMAIL")
directus_password = os.getenv("DIRECTUS_PASSWORD")
directus_instance = os.getenv("DIRECTUS_INSTANCE")
directus_login = f"{directus_instance}/auth/login"

# Create a session object for making requests
session = requests.Session()

# Send a POST request to the login endpoint
response = session.post(directus_login, json={"email": directus_email, "password": directus_password})

# Test if connection is successful
if response.status_code == 200:
    # Stores the access token
    data = response.json()["data"]
    directus_token = data["access_token"]

    # Construct headers with authentication token
    headers = {"Authorization": f"Bearer {directus_token}", "Content-Type": "application/json"}

    # Retrieve ms informations

    directus_ms = f"{directus_instance}/items/Mass_Spectrometry_Analysis/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_ms}?limit=-1")

# Check if the request was successful
if response.status_code == 200:
    data = response.json()["data"]

# Ensure destination folder exists
os.makedirs(destination_folder, exist_ok=True)


def find_file_recursively(filename: str, root_folder: str) -> str | None:
    """
    Search for a file recursively within root_folder.
    Returns the full path to the file if found, otherwise None.
    """
    for dirpath, _, filenames in os.walk(root_folder):
        if filename in filenames:
            return str(os.path.join(dirpath, filename))
    return None


# Open and read the TSV file
with open(tsv_file_path, newline="") as file:
    reader = csv.DictReader(file, delimiter="\t")

    # Check if fieldnames is None
    if reader.fieldnames is None:
        raise ValueError("1")

    # List to store rows of successfully copied files
    copied_rows = []

    # Loop over each row in the TSV file
    for row in reader:
        file_name = row[column_name]
        source_file = find_file_recursively(file_name, source_folder)

        if source_file:
            destination_file = os.path.join(destination_folder, file_name)
            shutil.copy(source_file, destination_file)
            directus_patch = directus_ms + "/" + row[column_name]
            observation = {"added": True}
            response = session.patch(url=directus_patch, headers=headers, json=observation)

            # If file copied successfully, add row to copied_rows
            copied_rows.append(row)
        else:
            print(f"File {file_name} does not exist in {source_folder}")

# Write copied rows to a new TSV file
with open(destination_metadata, "w", newline="") as new_file:
    writer = csv.DictWriter(new_file, fieldnames=reader.fieldnames, delimiter="\t")
    writer.writeheader()
    writer.writerows(copied_rows)


print("Operation completed.")
