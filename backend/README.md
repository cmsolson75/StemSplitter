# StemSplitter Backend

FastAPI backend for **StemSplitter**, providing AI-powered stem separation using [Demucs v4](https://github.com/facebookresearch/demucs).
This service processes uploaded audio files and returns separated stems (`vocals`, `drums`, `bass`, `other`) as high-quality WAV files in a ZIP archive.

---

## Features

* **REST API** for audio stem separation
* Supports multiple input formats: WAV, MP3, FLAC, M4A, AIFF, OGG
* Uses Facebook’s **Demucs v4** model (GPU or CPU)
* **Asynchronous** request handling with FastAPI
* Configurable via `config.yml`
* Docker-ready (GPU and CPU images)

---

## Requirements

* Python 3.10+ (if running without Docker)
* [ffmpeg](https://ffmpeg.org/) installed and available in `$PATH`
* Docker (for containerized runs)
* NVIDIA GPU with CUDA 11+ (optional for GPU acceleration)

---

## Development Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run backend (CPU mode)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run backend (GPU mode)

Ensure you have the NVIDIA Container Toolkit installed:

```bash
docker run --gpus all nvidia/cuda:11.8-base nvidia-smi
```

Then:

```bash
make up-gpu
```

---

## Configuration

Edit `config.yml` in the backend directory:

```yaml
model:
  name: "htdemucs"  # Options: htdemucs, htdemucs_ft, hdemucs_mmi

audio:
  supported_formats: [".wav", ".mp3", ".flac", ".m4a", ".aiff", ".ogg"]
  max_file_size: 100  # MB

api:
  title: "StemSplitter API"
  cors_origins: ["http://localhost:3000"]
```

---

## API Usage

**Docs:**
[http://localhost:8000/docs](http://localhost:8000/docs)

**Health check:**
[http://localhost:8000/health](http://localhost:8000/health)

**Separate audio (example with curl):**

```bash
curl -X POST "http://localhost:8000/separate" \
     -H "accept: application/zip" \
     -F "file=@your-audio.mp3" \
     -o stems.zip
```

---

## Testing

```bash
pytest -q
```

To test with sample audio:

```bash
cd tests/e2e/assets
# Upload one of the provided test files via the API or frontend
```

---

## Folder Structure

```
backend/
├── main.py           # FastAPI entrypoint
├── config.yml        # Backend configuration
├── requirements.txt  # Python dependencies
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core config and utilities
│   ├── services/     # Stem separation logic
│   └── models/       # AI model integration
└── tests/            # Unit and E2E tests
```

---

## Notes

* For best performance, run in GPU mode with a supported NVIDIA GPU.
* Audio is processed in-memory; ensure Docker memory limits are sufficient for large files.
* Output is always high-quality WAV, packaged in a ZIP.
