from google.cloud import storage
from google.api_core.exceptions import NotFound
from datetime import timedelta
from infra.config import get_settings
import uuid
import mimetypes
import logging
from infra.credential_manager import GoogleCredentialManager
import os
from io import BytesIO



class GCSFileRepository:
    """
    Implementation of FileRepository for Google Cloud Storage (GCS).
    """

    def __init__(self, bucket_name: str, client: storage.Client):
        """
        Initialize the GCSFileRepository with a given configuration and GCS client.

        Args:
            config (Config): The configuration containing GCS credentials and bucket name.
            client (storage.Client): The Google Cloud Storage client.
        """
        self.logger = logging.getLogger("gcs_file_repository")
        self.bucket_name = bucket_name
        self.client = client
        self.bucket = self.client.bucket(self.bucket_name)

    def _set_content_type(self, file_type: str) -> str:
        """
        Determine the MIME type of a file based on its extension.

        Args:
            file_type (str): The file extension (e.g, ".wav").

        Returns:
            str: The MIME type of the file.
        """
        if file_type.lower() == ".wav":
            return "audio/wav"
        if file_type.lower() == ".zip":
            return "application/zip"
        return (
            mimetypes.guess_type(f"dummy{file_type}")[0] or "application/octet-stream"
        )

    def _get_blob(self, file_url: str) -> storage.Blob:
        """
        Retrieve a Blob object from GCS for a given file URL.

        Args:
            file_url (str): The GCS URL of the file.

        Returns:
            storage.Blob: The Blob object representing the file.

        Raises:
            ValueError: If the URL is invalid or the bucket does not match.
        """
        if not file_url.startswith("gs://"):
            raise ValueError(f"Invalid GCS URL: {file_url}")

        _, _, bucket_name, *blob_path = file_url.split("/")
        if bucket_name != self.bucket_name:
            raise ValueError(
                f"Bucket mismatch: expected {self.bucket_name}, got {bucket_name}"
            )

        blob_name = "/".join(blob_path)
        return self.bucket.blob(blob_name)

    def upload_file(self, file_bytes: bytes, file_type: str = "wav", is_temporary: bool = False) -> str:
        """
        Upload a single file to GCS.

        Args:
            file_bytes (bytes): The file data to upload.
            file_type (str): The file type/extension (default is "wav").

        Returns:
            str: The GCS URL of the uploaded file.
        """
        if not file_type.startswith("."):
            file_type = f".{file_type}"

        content_type = self._set_content_type(file_type)
        folder = "temp/" if is_temporary else "files/"
        blob_name = f"{folder}file_{uuid.uuid4()}{file_type}"
        blob = self.bucket.blob(blob_name)
        try:
            stream= BytesIO(file_bytes)
            print(stream)
            blob.upload_from_file(
                stream,
                rewind=True,
                content_type=content_type,
                timeout=300
            )
            # blob.upload_from_string(file_bytes, content_type=content_type)
            file_url = f"gs://{self.bucket_name}/{blob_name}"
            self.logger.info(f"File uploaded successfully: {file_url}")
            return file_url
        
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}")
            raise

    def download_file(self, file_url: str) -> bytes:
        """
        Download a single file from GCS.

        Args:
            file_url (str): The GCS URL of the file.

        Returns:
            bytes: The file data in bytes.
        """
        blob = self._get_blob(file_url)
        try:
            return blob.download_as_bytes()
        except NotFound:
            self.logger.warning(f"File not found: {file_url}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error downloading file: {file_url} - {e}")
            raise

    def delete_file(self, file_url: str) -> None:
        """
        Delete a file from GCS.

        Args:
            file_url (str): The GCS URL of the file to delete.
        """
        blob = self._get_blob(file_url)
        try:
            blob.delete()
            logging.info(f"File successfully deleted: {file_url}")
        except NotFound:
            logging.warning(f"File not found: {file_url}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error deleting file: {file_url} - {e}")
            raise

    def generate_signed_url(
        self, file_url: str, expiration: int = 15, method: str = "GET"
    ) -> str:
        """
        Generate a signed URL for accessing a file

        Args:
            file_url (str): The GCS URL of the file.
            experation (int): Duration (in minutes) for which the signed URL is valid (default is 15).
            method (str): HTTP method for which the signed URL is valid (default is "GET")

        Returns:
            str: The signed URL for accessing the file.
        """
        blob = self._get_blob(file_url)
        try:
            signed_url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration),
                method=method,
            )
            self.logger.info(f"Generated signed URL for {file_url}: {signed_url}")
            return signed_url
        except Exception as e:
            self.logger.error(f"Failed to generate signed URL for {file_url}: {e}")
            raise


def create_gcs_file_repository():
    impersonation_account = os.getenv("IMPERSONATION_ACCOUNT")  # or hardcode for testing
    bucket_name = os.getenv("GCS_BUCKET_NAME", "stem-splitter-bucket")
    env = os.getenv("ENV", "local")
    print(impersonation_account)

    credential_manager = GoogleCredentialManager(
        env=env, impersonation_account=impersonation_account
    )
    credentials = credential_manager.get_credentials()
    gcs_client = storage.Client(credentials=credentials)
    return GCSFileRepository(bucket_name, gcs_client)