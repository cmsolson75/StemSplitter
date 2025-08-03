from fastapi.responses import StreamingResponse
from infra.file_repo import create_file_repository  # rename as needed

class FileStorageService:
    def __init__(self):
        self.repo = create_file_repository()

    def store_file(self, file_bytes: bytes, file_type: str = "zip") -> str:
        return self.repo.upload_file(file_bytes, file_type=file_type, is_temporary=True)

    def stream_file(self, file_path: str, filename: str = "output.zip") -> StreamingResponse:
        return self.repo.get_streaming_response(file_path, filename)