import zipfile
import pytest
import asyncio
import shutil
from pathlib import Path

# Check if ffmpeg is available (needed for M4A support)
def check_ffmpeg_available():
    """Check if ffmpeg is available on the system."""
    return shutil.which("ffmpeg") is not None

# All supported audio formats with their MIME types
AUDIO_FORMATS = [
    ("test_audio.wav", "audio/wav"),
    ("test_audio.mp3", "audio/mpeg"),
    ("test_audio.aif", "audio/aiff"),
    ("test_audio.aiff", "audio/aiff"),
    ("test_audio.m4a", "audio/mp4"),
    ("test_audio.flac", "audio/flac"),
    ("test_audio.ogg", "audio/ogg"),
]

@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.parametrize("filename, mime_type", AUDIO_FORMATS)
async def test_audio_separation_all_formats(test_client, tmp_path, filename, mime_type):
    """Test audio separation endpoint with various audio formats"""
    input_path = Path(f"tests/e2e/assets/{filename}")
    output_zip_path = tmp_path / f"{filename}_output.zip"
    
    # Ensure the test file exists
    assert input_path.exists(), f"Test audio file {input_path} not found"
    
    # Skip M4A test if ffmpeg is not available
    if filename.endswith(".m4a") and not check_ffmpeg_available():
        pytest.skip("ffmpeg not available, skipping M4A test")
    
    # Send the audio file to the separation endpoint
    with open(input_path, "rb") as f:
        files = {"file": (filename, f, mime_type)}
        response = await test_client.post("/separate", files=files)
    
    # Verify response
    assert response.status_code == 200, f"Failed for {filename}: {response.text}"
    assert response.headers["content-type"] == "application/zip"
    assert response.content and len(response.content) > 0, f"Empty response for {filename}"
    
    # Save and verify ZIP contents
    with open(output_zip_path, "wb") as out:
        out.write(response.content)
    
    with zipfile.ZipFile(output_zip_path, "r") as z:
        namelist = z.namelist()
        assert len(namelist) == 4, f"Expected 4 files, got {len(namelist)} for {filename}"
        assert all(name.endswith(".wav") for name in namelist), f"Not all outputs are WAV files for {filename}"
        
        # Verify each output file has content
        for name in namelist:
            with z.open(name) as audio_file:
                content = audio_file.read()
                assert len(content) > 0, f"Empty audio file {name} in output for {filename}"