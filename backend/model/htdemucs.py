import os
import tempfile
import torch
import torchaudio
import zipfile
from demucs.apply import apply_model
from torchaudio.transforms import Resample


class DemucsWrapper:
    def __init__(self, model_name="htdemucs"):
        from demucs.pretrained import get_model
        self.model = get_model(model_name).cpu().eval()
        self.device = torch.device("cpu")  # default to CPU for now
        self.model.to(self.device)

    def separate(self, audio_bytes: bytes) -> bytes:
        print("Separating")
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.wav")
            with open(input_path, "wb") as f:
                f.write(audio_bytes)

            waveform, sr = torchaudio.load(input_path)
            print("Loaded waveform")

            # Do not convert to mono — keep stereo for Demucs
            if sr != 44100:
                resampler = Resample(orig_freq=sr, new_freq=44100)
                waveform = resampler(waveform)
                sr = 44100

            waveform = waveform.unsqueeze(0).to(self.device)  # [1, C, T]

            with torch.no_grad():
                sources = apply_model(self.model, waveform, progress=True)

            sources = sources.squeeze(0)
            print(f"Extracted {sources.shape}")

            zip_path = os.path.join(tmpdir, "stems.zip")
            with zipfile.ZipFile(zip_path, "w") as zf:
                for i, name in enumerate(self.model.sources):
                    audio = sources[i]
                    stem_path = os.path.join(tmpdir, f"{name}.wav")
                    torchaudio.save(stem_path, audio.cpu(), sr)
                    zf.write(stem_path, arcname=f"{name}.wav")

            with open(zip_path, "rb") as f:
                return f.read()