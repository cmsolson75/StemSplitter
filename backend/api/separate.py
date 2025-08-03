from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from services.file_storage_service import FileStorageService
from services.model_service import model_service
import asyncio
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
storage_service = FileStorageService()

SUPPORTED_EXTENSIONS = (".wav", ".mp3", ".aif", ".aiff", ".m4a")


@router.post("/separate", response_class=Response)
async def separate(file: UploadFile = File(...)) -> Response:
    """
    Separate a single audio file into its source stems using Demucs.

    Accepts a WAV, MP3, AIFF, or M4A upload, runs inference, and returns a ZIP stream
    containing separated audio stems (e.g., drums, bass, vocals, other).

    Returns:
        StreamingResponse or RedirectResponse: depending on the backend implementation.
    Raises:
        HTTPException: if the file format is invalid or inference fails.
    """
    if not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Must be one of: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    audio_bytes = await file.read()

    try:
        zip_bytes = await model_service.run_inference(audio_bytes)
        file_path = await asyncio.to_thread(storage_service.store_file, zip_bytes, "zip")
        return await asyncio.to_thread(storage_service.stream_file, file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")