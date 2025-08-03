import os
import uuid
from io import BytesIO
from fastapi.responses import StreamingResponse


class FileRepository:
    """
    Simple local file repository using the /tmp directory. Suitable for ephemeral environments
    like Cloud Run, where persistent storage is not required.
    """

    def __init__(self, base_dir: str = "/tmp"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_file(self, file_bytes: bytes, file_type: str = "wav", is_temporary: bool = False) -> str:
        """
        Save the uploaded file to the local file system.

        Args:
            file_bytes (bytes): The binary content of the file.
            file_type (str): File extension, e.g., 'wav', 'zip'.
            is_temporary (bool): Determines if file goes into temp/ or files/.

        Returns:
            str: Full file path of the stored file.
        """
        if not file_type.startswith("."):
            file_type = f".{file_type}"

        folder = "temp" if is_temporary else "files"
        full_dir = os.path.join(self.base_dir, folder)
        os.makedirs(full_dir, exist_ok=True)

        file_id = f"file_{uuid.uuid4()}{file_type}"
        file_path = os.path.join(full_dir, file_id)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return file_path

    def get_streaming_response(self, file_url: str, filename: str = "output.zip") -> StreamingResponse:
        """
        Stream a file as a downloadable response.

        Args:
            file_url (str): Full local file path.
            filename (str): Filename to present in the download prompt.

        Returns:
            StreamingResponse: FastAPI response object with file stream.
        """
        if not os.path.exists(file_url):
            raise FileNotFoundError(f"{file_url} does not exist")

        with open(file_url, "rb") as f:
            return StreamingResponse(
                BytesIO(f.read()),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )


def create_file_repository() -> FileRepository:
    """
    Instantiate the local file repository for /tmp storage.
    """
    return FileRepository(base_dir="/tmp")