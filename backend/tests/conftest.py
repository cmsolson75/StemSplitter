import os
import sys
import pytest
import pytest_asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from main import app
from tests.utils.audio import trim_audio


# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="function")
def test_audio_path(tmp_path) -> Path:
    input_path = Path("tests/e2e/assets/DefaultSet.wav")
    output_path = tmp_path / "short_test.wav"
    return trim_audio(input_path, output_path, duration_ms=2000)


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="module")
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client