import zipfile
import pytest
import asyncio
from pathlib import Path

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_separate_stream_response(test_client, test_audio_path, tmp_path):
    output_zip_path = tmp_path / "output.zip"

    with open(test_audio_path, "rb") as f:
        files = {"file": ("short.wav", f, "audio/wav")}
        response = await test_client.post("/separate", files=files)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    with open(output_zip_path, "wb") as out:
        out.write(response.content)

    with zipfile.ZipFile(output_zip_path, "r") as z:
        namelist = z.namelist()
        assert len(namelist) == 4  # e.g., drums, bass, other, vocals
        assert all(name.endswith(".wav") for name in namelist)

# FORMATS = [
#     ("DefaultSet.wav", "audio/wav"),
#     ("DefaultSet.mp3", "audio/mpeg"),
#     ("DefaultSet.aif", "audio/aiff"),
#     ("DefaultSet.aiff", "audio/aiff"),
#     ("DefaultSet.m4a", "audio/mp4"),
# ]

# @pytest.mark.asyncio
# @pytest.mark.e2e
# @pytest.mark.parametrize("filename, mime", FORMATS)
# async def test_supported_audio_formats(test_client, tmp_path, filename, mime):
#     input_path = Path(f"tests/e2e/assets/{filename}")
#     output_path = tmp_path / f"{filename}.zip"

#     with open(input_path, "rb") as f:
#         files = {"file": (filename, f, mime)}
#         response = await test_client.post("/separate", files=files)

#     assert response.status_code == 200
#     assert response.headers["content-type"] == "application/zip"

#     # Basic check — output should be non-empty
#     assert response.content and len(response.content) > 0

#     # Optional: check ZIP structure
#     with open(output_path, "wb") as out:
#         out.write(response.content)
#     with zipfile.ZipFile(output_path, "r") as z:
#         assert len(z.namelist()) == 4
#         assert all(name.endswith(".wav") for name in z.namelist())