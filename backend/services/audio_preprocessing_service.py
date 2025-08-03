from pydub import AudioSegment
from io import BytesIO
import torchaudio


class AudioPreprocessingService:
    """
    Handles decoding and normalization of various audio formats to WAV-compatible tensors.
    """

    def __init__(self, target_sr: int = 44100):
        self.target_sr = target_sr

    def decode(self, audio_bytes: bytes) -> tuple:
        """
        Ensures audio is decoded to a torch.Tensor in WAV-compatible format.

        Returns:
            tuple[Tensor, int]: (waveform, sample_rate)
        """
        try:
            # Try decoding directly
            with BytesIO(audio_bytes) as buf:
                return torchaudio.load(buf)
        except Exception:
            # Fallback to ffmpeg + pydub for format conversion
            audio = AudioSegment.from_file(BytesIO(audio_bytes))
            audio = audio.set_frame_rate(self.target_sr).set_channels(2).set_sample_width(2)
            wav_io = BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            return torchaudio.load(wav_io)