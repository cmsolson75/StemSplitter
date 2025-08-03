import os
import tempfile
import torch
import torchaudio
import zipfile
from typing import Optional
from torch import Tensor
from demucs.apply import apply_model
from torchaudio.transforms import Resample
from demucs.pretrained import get_model
import torchaudio

class DemucsWrapper:
    """
    Wrapper around the Demucs model for audio source separation.
    
    This class loads a pretrained Demucs model and exposes a method to separate
    audio files into individual source stems (e.g., drums, bass, vocals, other).
    
    It outputs a ZIP archive containing the separated WAV files.
    """

    def __init__(self, model_name: str = "htdemucs"):
        """
        Initialize the wrapper with a given pretrained model.

        Args:
            model_name (str): The name of the Demucs model to load.
        """
        self.device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = get_model(model_name).to(self.device).eval()

    def separate(self, audio_bytes: bytes) -> bytes:
        """
        Perform source separation on an input audio file.

        Args:
            audio_bytes (bytes): Raw audio file content (must be WAV or MP3 format).

        Returns:
            bytes: A ZIP archive containing the separated source stems as WAV files.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.wav")
            with open(input_path, "wb") as f:
                f.write(audio_bytes)

            waveform, original_sr = torchaudio.load(input_path)

            # Convert to target sample rate for Demucs
            if original_sr != 44100:
                resampler = Resample(orig_freq=original_sr, new_freq=44100)
                waveform = resampler(waveform)

            waveform = waveform.unsqueeze(0).to(self.device)  # Shape: [1, channels, time]

            with torch.no_grad():
                sources: Tensor = apply_model(self.model, waveform, progress=False)

            sources = sources.squeeze(0)  # Shape: [num_sources, channels, time]

            zip_path = os.path.join(tmpdir, "stems.zip")
            with zipfile.ZipFile(zip_path, "w") as zf:
                for i, name in enumerate(self.model.sources):
                    audio = sources[i]
                    stem_path = os.path.join(tmpdir, f"{name}.wav")
                    torchaudio.save(stem_path, audio.cpu(), 44100)
                    zf.write(stem_path, arcname=f"{name}.wav")

            with open(zip_path, "rb") as f:
                return f.read()