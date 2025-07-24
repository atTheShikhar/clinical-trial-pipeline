from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime, timedelta
from typing import Optional

from src.settings import sm


class Storage:
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        """
        Initialize the Storage client with bucket and optional credentials.

        Args:
            bucket_name (str): Name of the Google Cloud Storage bucket.
            credentials_path (str, optional): Path to service account JSON. If None, uses default credentials.
        """
        self.bucket_name = bucket_name

        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = storage.Client(credentials=credentials)
        else:
            self.client = storage.Client()

        self.bucket = self.client.bucket(bucket_name)

    def generate_signed_upload_url(self, blob_name: str, expiration_minutes: int = 15) -> str:
        """
        Generate a signed URL for uploading a file via HTTP PUT.

        Args:
            blob_name (str): Path of the object to be uploaded.
            expiration_minutes (int): Validity of the signed URL in minutes.

        Returns:
            str: Signed URL for file upload.
        """
        blob = self.bucket.blob(blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="PUT",
            content_type="application/octet-stream"
        )

    def generate_signed_view_url(self, blob_name: str, expiration_minutes: int = 15) -> str:
        """
        Generate a signed URL for viewing/downloading a file via HTTP GET.

        Args:
            blob_name (str): Path of the object to be viewed.
            expiration_minutes (int): Validity of the signed URL in minutes.

        Returns:
            str: Signed URL for viewing/downloading the file.
        """
        blob = self.bucket.blob(blob_name)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )

    def file_exists(self, blob_name: str) -> tuple[bool, Optional[datetime]]:
        """
        Check if a file exists in the GCS bucket and return its creation timestamp.

        Args:
            blob_name (str): Path of the object to check.

        Returns:
            Tuple[bool, Optional[str]]: 
                - True and creation timestamp in ISO format if file exists
                - False and None if file does not exist
        """
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            blob.reload()  # Load metadata
            created_at = blob.time_created if blob.time_created else None
            return True, created_at
        else:
            return False, None


storage_client = Storage(bucket_name=sm.storage_bucket, credentials_path="./gcs_creds.json")