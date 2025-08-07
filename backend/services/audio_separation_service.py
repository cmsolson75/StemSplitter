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
        
        # Preprocess audio in background thread
        try:
            preprocessed_audio = await asyncio.to_thread(
                self.processor.preprocess_audio, 
                audio_bytes, 
                filename
            )
        except ValueError as e:
            raise ValueError(f"Audio preprocessing failed: {str(e)}")
        
        # Run separation in background thread
        try:
            return await asyncio.to_thread(self.model.separate, preprocessed_audio)
        except Exception as e:
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