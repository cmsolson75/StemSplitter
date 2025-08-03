from model.htdemucs import DemucsWrapper
from services.audio_preprocessing_service import AudioPreprocessingService
import asyncio

# Could be inference service.
class ModelService:
    """
    Simple wrapper for running Demucs inference with caching and async-to-thread support.
    """

    def __init__(self):
        self.model = DemucsWrapper()

    async def run_inference(self, audio_bytes: bytes) -> bytes:
        """
        Run Demucs separation in a background thread.

        Args:
            audio_bytes (bytes): Raw audio input.

        Returns:
            bytes: ZIP archive of separated stems.
        """
        return await asyncio.to_thread(self.model.separate, audio_bytes)


# Singleton instance
model_service = ModelService()