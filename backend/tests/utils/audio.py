from pydub import AudioSegment
from pathlib import Path

def trim_audio(input_path: Path, output_path: Path, duration_ms: int = 2000) -> Path:
    audio = AudioSegment.from_file(input_path)
    trimmed = audio[:duration_ms]
    trimmed.export(output_path, format="wav")
    return output_path