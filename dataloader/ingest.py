import requests
import zipfile
import io
import os
from google.cloud import storage
from google.api_core import exceptions as gcp_exceptions
import concurrent.futures

from dotenv import load_dotenv

load_dotenv()

# --- Configuration for Concurrent Uploads ---
# The number of files to upload in parallel.
# Adjust this based on your network speed and the number of CPU cores.
# A good starting point is between 4 and 16.
MAX_WORKERS = 4

def upload_worker(bucket, blob_name, data_stream):
    """
    Worker function to upload a single file's data to GCS.
    This function is executed by each thread in the pool.
    """
    try:
        blob = bucket.blob(blob_name)
        # The data_stream is a file-like object from the zip archive.
        # We need to read its content to pass it to the upload function.
        blob.upload_from_string(data_stream.read())
        return None # Return None on success
    except Exception as e:
        print(f"FAILED to upload {blob_name}: {e}")
        return e # Return the exception on failure

def download_extract_and_upload(zip_url, bucket_name, destination_folder=''):
    """
    Downloads a ZIP file, and concurrently uploads its contents to GCS.
    """
    print(f"Starting process for URL: {zip_url}")
    print(f"Target GCS Bucket: {bucket_name}")
    print(f"Using up to {MAX_WORKERS} parallel workers for uploads.")

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        print("Downloading ZIP file into memory...")
        response = requests.get(zip_url)
        response.raise_for_status()
        zip_in_memory = io.BytesIO(response.content)
        print("✅ ZIP file downloaded.")

        failed_uploads = []
        with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
            file_list = [f for f in zip_ref.infolist() if not f.is_dir()]
            print(f"Found {len(file_list)} files to upload from the archive.")
            
            # Use a ThreadPoolExecutor to manage concurrent uploads
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Create a dictionary to map futures to filenames
                future_to_file = {}
                for member in file_list:
                    blob_name = os.path.join(destination_folder, member.filename).replace("\\", "/")
                    file_data_stream = zip_ref.open(member.filename)
                    
                    # Submit the upload task to the thread pool
                    future = executor.submit(upload_worker, bucket, blob_name, file_data_stream)
                    future_to_file[future] = member.filename

                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_file):
                    filename = future_to_file[future]
                    result = future.result()
                    if result: # If an exception was returned
                        failed_uploads.append(filename)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid ZIP archive.")
    except gcp_exceptions.GoogleAPICallError as e:
        print(f"An error occurred with the Google Cloud API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    else:
        print("\n--- Upload Summary ---")
        if not failed_uploads:
            print("All files were successfully uploaded!")
        else:
            print(f"{len(failed_uploads)} file(s) failed to upload:")
            for f in failed_uploads:
                print(f"  - {f}")


if __name__ == "__main__":
    SOURCE_ZIP_URL = 'https://clinicaltrials.gov/api/v2/studies/download?format=json.zip'
    GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
    DESTINATION_GCS_FOLDER = ''

    download_extract_and_upload(SOURCE_ZIP_URL, GCS_BUCKET_NAME, DESTINATION_GCS_FOLDER)
