# StemSplitter

> **AI-powered audio stem separation that just works**

Separate any audio track into individual stems (drums, bass, vocals, other) using state-of-the-art AI. Built with Facebook's Demucs model and wrapped in a beautiful, modern web interface.

## Features

- **One-click separation** - Upload audio, get stems
- **AI-powered** - Uses Facebook's Demucs v4 model
- **Beautiful UI** - Modern React interface with real-time progress
- **Fast processing** - GPU accelerated (with CPU fallback)
- **Multiple formats** - WAV, MP3, FLAC, M4A, AIFF, OGG
- **Docker ready** - Single command deployment
- **Configurable** - Easy YAML configuration
- **Responsive** - Works on desktop and mobile

## Quick Start

**Choose your hardware:**

```bash
git clone https://github.com/cmsolson75/StemSplitter.git
cd StemSplitter

# For NVIDIA GPU users
make up-gpu

# For everyone else (CPU)
make up-cpu
```

Then open http://localhost:3000 and start separating audio.

### Development Setup

```bash
make install  # Install dependencies
make dev      # Start both services locally
```

## Requirements

**Hardware Support:**
- **NVIDIA GPU** (GTX 1060+ recommended) - Fast GPU acceleration
- **Apple Silicon** (M1/M2/M4 Macs) - Optimized CPU processing
- **Intel/AMD CPU** (4+ cores recommended) - Works on any modern CPU

**System Requirements:**
- 4GB RAM (8GB+ recommended for large files)
- 2GB free disk space
- Docker & Docker Compose
- Modern web browser

## Usage

1. **Upload** your audio file (drag & drop or browse)
2. **Wait** for AI processing (30 seconds - 5 minutes depending on length)
3. **Download** the ZIP containing separated stems:
   - `drums.wav` - Drum track
   - `bass.wav` - Bass line
   - `vocals.wav` - Vocal track  
   - `other.wav` - Everything else (guitars, keys, etc.)

## Supported Formats

**Input:** WAV, MP3, FLAC, M4A, AIFF, OGG  
**Output:** High-quality WAV stems in ZIP archive

## Configuration

Edit `config.yml` to customize your setup:

```yaml
# Model settings
model:
  name: "htdemucs"  # Available: htdemucs, htdemucs_ft, hdemucs_mmi

# Audio settings  
audio:
  supported_formats: [".wav", ".mp3", ".flac", ".m4a", ".aiff", ".ogg"]
  max_file_size: 100  # MB

# API settings
api:
  title: "StemSplitter API"
  cors_origins: ["http://localhost:3000"]
```

**Quick config commands:**
```bash
make config      # View current config
make edit-config # Edit config file
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│                 │────▶│                  │
│  React Frontend │     │  FastAPI Backend │
│  (Port 3000)    │◀────│  (Port 8000)     │
│                 │     │                  │
└─────────────────┘     └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │                  │
                        │  Demucs AI Model │
                        │  (GPU/CPU)       │
                        │                  │
                        └──────────────────┘
```

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python with async processing
- **AI Model**: Facebook Demucs v4 (hybrid transformer)
- **Deployment**: Docker Compose with GPU support

## Deployment

### Local Development
```bash
make dev        # Start both frontend and backend locally
make test       # Run tests
make clean      # Clean up Docker resources
```

### Production with Docker
```bash
make build      # Build images
make up-gpu     # Start with GPU
make up-cpu     # Start CPU-only
make logs       # View logs
make down       # Stop services
```

### Check System Status
```bash
make status     # Show running services and system info
```

## API Documentation

Once running, visit:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### API Endpoints

```bash
POST /separate
Content-Type: multipart/form-data

# Upload audio file and get separated stems as ZIP
curl -X POST "http://localhost:8000/separate" \
     -H "accept: application/zip" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-audio.mp3"
```

## Testing

```bash
# Run backend tests
make test

# Test with sample audio
cd backend/tests/e2e/assets
# Upload any of the test_audio.* files via the web interface
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow TypeScript/Python best practices
- Add tests for new features
- Update documentation
- Use conventional commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Facebook Research** - For the incredible [Demucs](https://github.com/facebookresearch/demucs) model
- **Hugging Face** - For model hosting and transformers library
- **FastAPI** - For the amazing Python web framework
- **Vercel** - For Next.js and deployment inspiration

## Support

- **Bug reports**: [Open an issue](https://github.com/cmsolson75/StemSplitter/issues)
- **Feature requests**: [Start a discussion](https://github.com/cmsolson75/StemSplitter/discussions)
- **Email**: your-email@example.com

## Example Results

Upload a song and get professional-quality stems:

```
your-song.mp3 (3:45, 8.2MB)
    ↓ Processing with AI...
your-song_separated.zip
├── drums.wav    (Isolated drum track)
├── bass.wav     (Bass line only)  
├── vocals.wav   (Clean vocals)
└── other.wav    (Guitars, keys, etc.)
```

## Troubleshooting

**Common Issues:**

- **"Failed to fetch"** → Make sure backend is running on port 8000
- **Slow processing** → Use GPU mode with `make up-gpu` if you have NVIDIA GPU
- **Out of memory** → Reduce file size or increase Docker memory limit
- **Unsupported format** → Convert to WAV/MP3 first

**Performance Tips:**

- Use WAV format for best quality
- Keep files under 10 minutes for faster processing
- Use GPU mode when available
- Close other applications during processing

---

**Made with love for musicians, producers, and audio enthusiasts**

*Star this repo if it helped you create something awesome!*