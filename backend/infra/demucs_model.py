import os
import tempfile
import torch
import torchaudio
import zipfile
from typing import Dict, List
from torch import Tensor
from demucs.apply import apply_model
from torchaudio.transforms import Resample
from demucs.pretrained import get_model
from config_loader import config


class DemucsModel:
    """
    This class loads a pretrained Demucs model and provides audio source separation
    functionality. It expects preprocessed WAV audio input and outputs a ZIP archive
    containing the separated stems.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize the Demucs model.

        Args:
            model_name (str): The name of the Demucs model to load. If None, uses config.
        """
        # Only change: get model name from config if not provided
        print(f"🔵 Initializing Demucs model: {model_name}")
        self.model_name = model_name or config.get("model.name", "htdemucs")
        print(f"🔵 Using model: {self.model_name}")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔵 Using device: {self.device}")
        
        print("🔵 Loading model...")
        self.model = get_model(self.model_name).to(self.device).eval()
        print("✅ Model loaded successfully!")


    def separate(self, audio_bytes: bytes) -> bytes:
        """
        Perform source separation on preprocessed WAV audio.

        Args:
            audio_bytes (bytes): Raw WAV audio file content (should be preprocessed).

        Returns:
            bytes: A ZIP archive containing the separated source stems as WAV files.
            
        Raises:
            Exception: If audio loading or separation fails.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.wav")
            
            # Write input audio to temporary file
            with open(input_path, "wb") as f:
                f.write(audio_bytes)

            try:
                # Load audio with torchaudio
                waveform, original_sr = torchaudio.load(input_path)
            except Exception as e:
                raise Exception(f"Failed to load audio: {str(e)}")

            # Convert to target sample rate for Demucs (44.1kHz)
            if original_sr != 44100:
                resampler = Resample(orig_freq=original_sr, new_freq=44100)
                waveform = resampler(waveform)

            # Prepare waveform for model input
            waveform = waveform.unsqueeze(0).to(self.device)  # Shape: [1, channels, time]

            try:
                # Run separation
                with torch.no_grad():
                    sources: Tensor = apply_model(self.model, waveform, progress=False)
            except Exception as e:
                raise Exception(f"Demucs separation failed: {str(e)}")

            # Remove batch dimension
            sources = sources.squeeze(0)  # Shape: [num_sources, channels, time]

            # Create ZIP archive with separated stems
            zip_path = os.path.join(tmpdir, "stems.zip")
            try:
                with zipfile.ZipFile(zip_path, "w") as zf:
                    for i, name in enumerate(self.model.sources):
                        audio = sources[i]
                        stem_path = os.path.join(tmpdir, f"{name}.wav")
                        
                        # Save stem as WAV file
                        torchaudio.save(stem_path, audio.cpu(), 44100)
                        
                        # Add to ZIP archive
                        zf.write(stem_path, arcname=f"{name}.wav")

                # Read and return ZIP bytes
                with open(zip_path, "rb") as f:
                    return f.read()
                    
            except Exception as e:
                raise Exception(f"Failed to create output ZIP: {str(e)}")

    def get_source_names(self) -> List[str]:
        """
        Get the names of the audio sources this model separates.
        
        Returns:
            List[str]: List of source names from the loaded Demucs model.
        """
        return list(self.model.sources)

    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the Demucs model.
        
        Returns:
            Dict[str, str]: Model information including name, device, and sources.
        """
        return {
            "name": self.model_name,
            "device": str(self.device),
            "sources": ", ".join(self.model.sources),
            "sample_rate": "44100",
            "type": "Demucs"
        }