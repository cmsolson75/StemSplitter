from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from services.file_storage_service import FileStorageService
from services.audio_separation_service import audio_separation_service
import asyncio
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
storage_service = FileStorageService()


@router.post("/separate", response_class=Response)
async def separate(file: UploadFile = File(...)) -> Response:
    """
    Separate a single audio file into its source stems using Demucs.

    Accepts various audio formats (WAV, MP3, AIFF, M4A, FLAC, OGG), preprocesses them
    for optimal Demucs compatibility, runs inference, and returns a ZIP stream
    containing separated audio stems (e.g., drums, bass, vocals, other).

    Returns:
        Response: ZIP file containing separated audio stems.
    Raises:
        HTTPException: if the file format is invalid or processing fails.
    """
    # Validate file format using the service
    print(f"🔵 [START] Processing file: {file.filename}")
    if not file.filename or not audio_separation_service.is_supported_format(file.filename):
        supported_formats = ", ".join(audio_separation_service.supported_extensions)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Must be one of: {supported_formats}"
        )

    audio_bytes = await file.read()

    try:
        # Run audio separation
        print("🔵 [STEP 1] Reading file bytes...")
        audio_bytes = await file.read()
        print(f"✅ [STEP 1] Read {len(audio_bytes)} bytes")
        
        print("🔵 [STEP 2] Starting audio separation service...")
        zip_bytes = await audio_separation_service.separate_audio(audio_bytes, file.filename)
        print(f"✅ [STEP 2] Separation complete, ZIP size: {len(zip_bytes)} bytes")
        
        print("🔵 [STEP 3] Storing file...")
        file_path = await asyncio.to_thread(storage_service.store_file, zip_bytes, "zip")
        print(f"✅ [STEP 3] File stored at: {file_path}")
        
        print("🔵 [STEP 4] Creating streaming response...")
        response = await asyncio.to_thread(storage_service.stream_file, file_path)
        print("✅ [STEP 4] Streaming response created")
        
        print("🎉 [SUCCESS] Request completed successfully!")
        return response
        
    except ValueError as e:
        # Audio preprocessing errors (client error)
        error_msg = str(e)
        if "ffmpeg not found" in error_msg:
            raise HTTPException(
                status_code=500, 
                detail="Server configuration error: ffmpeg required for this audio format"
            )
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        # Other processing errors (server error)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")