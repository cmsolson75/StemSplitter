import os
import tempfile
import torchaudio
import torch
import subprocess
from config_loader import config


class AudioProcessor:
    """
    Audio processor that handles format conversion and preprocessing.
    
    Uses torchaudio as the primary processor and falls back to FFmpeg 
    for unsupported formats like M4A.
    """
    
    def __init__(self):
        # Only change: get supported extensions from config
        self.SUPPORTED_EXTENSIONS = tuple(config.get("audio.supported_formats", 
                                                     [".wav", ".mp3", ".aif", ".aiff", ".m4a", ".flac", ".ogg"]))
    
    def preprocess_audio(self, audio_bytes: bytes, original_filename: str = "input") -> bytes:
        """
        Preprocess audio bytes into a standardized WAV format.
        
        Args:
            audio_bytes (bytes): Raw audio file content in any supported format
            original_filename (str): Original filename for format detection
            
        Returns:
            bytes: Preprocessed audio as WAV format bytes
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Determine file extension for format detection
            file_ext = self._get_file_extension(original_filename)
            input_path = os.path.join(tmpdir, f"input{file_ext}")
            intermediate_path = os.path.join(tmpdir, "converted.wav")
            output_path = os.path.join(tmpdir, "preprocessed.wav")
            
            # Write input bytes to temporary file
            with open(input_path, "wb") as f:
                f.write(audio_bytes)
            
            # Try to load with torchaudio first
            try:
                waveform, sample_rate = torchaudio.load(input_path)
                use_ffmpeg_fallback = False
            except Exception as e:
                # If torchaudio fails, use FFmpeg to convert to WAV first
                print(f"torchaudio failed for {file_ext}, using ffmpeg fallback: {e}")
                use_ffmpeg_fallback = True
            
            if use_ffmpeg_fallback:
                # Use FFmpeg to convert to WAV format that torchaudio can handle
                self._convert_with_ffmpeg(input_path, intermediate_path)
                waveform, sample_rate = torchaudio.load(intermediate_path)
            
            # Normalize channels (ensure stereo)
            waveform = self._normalize_channels(waveform)
            
            # Ensure float32 format for consistency
            if waveform.dtype != torch.float32:
                waveform = waveform.float()
            
            # Save as standardized WAV file
            torchaudio.save(
                output_path, 
                waveform, 
                sample_rate,
                encoding="PCM_F",  # 32-bit float
                bits_per_sample=32
            )
            
            # Read and return the preprocessed bytes
            with open(output_path, "rb") as f:
                return f.read()
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if the given filename has a supported audio format."""
        if not filename:
            return False
        return filename.lower().endswith(self.SUPPORTED_EXTENSIONS)
    
    def _convert_with_ffmpeg(self, input_path: str, output_path: str) -> None:
        """Convert audio file to WAV using FFmpeg as a fallback."""
        try:
            cmd = [
                "ffmpeg", 
                "-i", input_path,
                "-ar", "44100",        # Set sample rate to 44.1kHz
                "-ac", "2",            # Convert to stereo
                "-acodec", "pcm_f32le", # 32-bit float PCM
                "-y",                  # Overwrite output file
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            raise ValueError(f"ffmpeg conversion failed: {e.stderr}")
        except FileNotFoundError:
            raise ValueError("ffmpeg not found. Please install ffmpeg to support M4A and other formats.")
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension, defaulting to .wav if unknown."""
        if not filename or "." not in filename:
            return ".wav"
        return os.path.splitext(filename.lower())[1]
    
    def _normalize_channels(self, waveform: torch.Tensor) -> torch.Tensor:
        """Normalize audio channels to stereo."""
        num_channels = waveform.shape[0]
        
        if num_channels == 1:
            # Convert mono to stereo by duplicating the channel
            waveform = waveform.repeat(2, 1)
        elif num_channels > 2:
            # Convert multi-channel to stereo by taking first 2 channels
            waveform = waveform[:2, :]
        
        return waveform