from fastapi import APIRouter, UploadFile, File, HTTPException
from infra.file_repo import create_gcs_file_repository
from infra.config import get_settings
from model.htdemucs import DemucsWrapper  # <- import your wrapper directly
import asyncio
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
settings = get_settings()
repo = create_gcs_file_repository()
model = DemucsWrapper()  # <- instantiate model directly (singleton)

@router.post("/separate")
async def separate(file: UploadFile = File(...)):
    if not file.filename.endswith((".wav", ".mp3")):
        raise HTTPException(status_code=400, detail="Only WAV or MP3 supported")

    try:
        audio_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    try:
        # Run model inference in thread
        zip_bytes = await asyncio.to_thread(model.separate, audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    try:
        gcs_path = await asyncio.to_thread(repo.upload_file, zip_bytes, ".zip")
        signed_url = await asyncio.to_thread(repo.generate_signed_url, gcs_path)
        return {"url": signed_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GCS error: {e}")