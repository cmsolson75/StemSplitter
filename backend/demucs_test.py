# tests/integration/test_demucs.py
from model.htdemucs import DemucsWrapper
from pathlib import Path

def run_demucs_test(input_path: str, output_path: str):
    model = DemucsWrapper()
    input_file = Path(input_path)
    assert input_file.exists(), f"Missing file: {input_file}"

    with input_file.open("rb") as f:
        audio_bytes = f.read()

    output_bytes = model.separate(audio_bytes)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("wb") as f:
        f.write(output_bytes) 

    print(f"✅ Wrote: {output_file.resolve()}")

if __name__ == "__main__":
    input_path = "/Users/cameronolson/Developer/Work/Echelon/Repos/StemSplitterTool/DefaultSet.wav"
    output = "test.zip"
    run_demucs_test(input_path, output)