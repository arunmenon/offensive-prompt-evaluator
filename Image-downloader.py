import requests
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to extract the unique identifier from the URL
def extract_filename_from_url(url):
    parsed_url = urlparse(url)
    # Extract the file name from the URL path (e.g., b71f95b0-a771-40ba-8caf-662266f1714d)
    filename = os.path.basename(parsed_url.path)
    # Remove the file extension (.jpeg) if present
    filename_without_extension = os.path.splitext(filename)[0]
    return filename_without_extension

# Function to download a single image
def download_image(url, download_folder):
    url = url.strip()
    if url:
        try:
            # Extract the unique identifier from the URL
            unique_filename = extract_filename_from_url(url)
            file_name = f"{unique_filename}.jpeg"
            file_path = os.path.join(download_folder, file_name)

            # Check if the file already exists
            if os.path.exists(file_path):
                print(f"File {file_name} already exists. Skipping download.")
                return

            # If the file does not exist, download it
            response = requests.get(url)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {file_name} from {url}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

# Function to download images concurrently from a list of URLs
def download_images_concurrently(file_path, download_folder, max_workers=5):
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Read the URLs from the text file and remove duplicates
    with open(file_path, 'r') as url_file:
        urls = list(set([url.strip() for url in url_file.readlines()]))

    # Use ThreadPoolExecutor to download images concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks to the executor
        futures = [executor.submit(download_image, url, download_folder) for url in urls]

        # Process the results as they complete
        for future in as_completed(futures):
            try:
                future.result()  # Retrieve result or raise an exception if it failed
            except Exception as e:
                print(f"An error occurred: {e}")

# Path to the text file containing the URLs
url_file_path = 'image_urls.txt'

# Folder to save the downloaded images
download_folder = 'downloaded_images'

# Call the function to download images concurrently
download_images_concurrently(url_file_path, download_folder, max_workers=5)
