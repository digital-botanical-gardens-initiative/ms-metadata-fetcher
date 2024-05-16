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
source_folder = os.getenv("SOURCE_FOLDER")
destination_folder = os.getenv("DESTINATION_FOLDER") + f"/subset_{datetime.now().strftime('%Y%m%d%H')}"
column_name = "sample_filename"  # Replace with the actual column name

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


def find_file_recursively(filename, root_folder):
    filename = filename
    """
    Search for a file recursively within root_folder.
    Returns the full path to the file if found, otherwise None.
    """
    for dirpath, _, filenames in os.walk(root_folder):
        if filename in filenames:
            return os.path.join(dirpath, filename)
    return None


# Open and read the TSV file
with open(tsv_file_path, newline="") as file:
    reader = csv.DictReader(file, delimiter="\t")

    # Loop over each row in the TSV file
    for row in reader:
        file_name = row[column_name] + ".mzML"
        source_file = find_file_recursively(file_name, source_folder)

        if source_file:
            destination_file = os.path.join(destination_folder, file_name)
            shutil.copy(source_file, destination_file)
            directus_patch = directus_ms + "/" + row[column_name]
            observation = {"added": True}
            response = session.patch(url=directus_patch, headers=headers, json=observation)
        else:
            print(f"File {file_name} does not exist in {source_folder}")

print("Operation completed.")
