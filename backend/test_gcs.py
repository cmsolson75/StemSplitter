from infra.file_repo import GCSFileRepository, create_gcs_file_repository
from infra.config import get_settings
from pathlib import Path
from google.cloud import storage

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    settings = get_settings()
    BUCKET_NAME = settings.gcs_bucket
    file_path = Path("/Users/cameronolson/Developer/Work/Echelon/Repos/StemSplitterTool/DefaultSet.wav")
    repo = create_gcs_file_repository()
    with open(file_path, "rb") as fs:
        data = fs.read()

    # Upload and generate signed URL
    gcs_url = repo.upload_file(data, file_type=".wav")
    signed_url = repo.generate_signed_url(gcs_url)

    print(f"GCS URL: {gcs_url}")
    print(f"Signed URL: {signed_url}")