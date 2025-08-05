import asyncio
from infra.demucs_model import DemucsModel
from infra.ffmpeg_processor import AudioProcessor


class AudioSeparationService:
    """
    Service for running audio source separation with preprocessing.
    
    Orchestrates the full pipeline: preprocessing -> separation -> output.
    """

    def __init__(self):
        self.model = DemucsModel()
        self.processor = AudioProcessor()

    async def separate_audio(self, audio_bytes: bytes, filename: str = "input") -> bytes:
        """
        Run audio separation with preprocessing in background threads.

        Args:
            audio_bytes (bytes): Raw audio input in any supported format.
            filename (str): Original filename for format detection.

        Returns:
            bytes: ZIP archive of separated stems.
            
        Raises:
            ValueError: If audio preprocessing fails.
            Exception: If audio separation fails.
        """
        print(f"🔵 [AUDIO SERVICE] Starting separation for: {filename}")
        print(f"🔵 [AUDIO SERVICE] Input size: {len(audio_bytes)} bytes")
        # Preprocess audio in background thread
        try:
            print("🔵 [PREPROCESSING] Starting audio preprocessing...")
            preprocessed_audio = await asyncio.to_thread(
                self.processor.preprocess_audio, 
                audio_bytes, 
                filename
            )
        except ValueError as e:
            print(f"❌ [PREPROCESSING] Failed: {str(e)}")
            raise ValueError(f"Audio preprocessing failed: {str(e)}")
        
        # Run separation in background thread
        try:
            print("🔵 [DEMUCS] Starting model separation...")
            result = await asyncio.to_thread(self.model.separate, preprocessed_audio)
            print(f"✅ [DEMUCS] Complete, result size: {len(result)} bytes")
            return result
        except Exception as e:
            print(f"❌ [DEMUCS] Failed: {str(e)}")
            print(f"❌ [DEMUCS] Error type: {type(e).__name__}")
            import traceback
            print(f"❌ [DEMUCS] Traceback: {traceback.format_exc()}")
            raise Exception(f"Audio separation failed: {str(e)}")

    def is_supported_format(self, filename: str) -> bool:
        """Check if the audio format is supported."""
        return self.processor.is_supported_format(filename)

    @property
    def supported_extensions(self) -> tuple:
        """Get supported file extensions."""
        return self.processor.SUPPORTED_EXTENSIONS


# Singleton instance
audio_separation_service = AudioSeparationService()