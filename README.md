
# StemSplitter

> AI-powered audio stem separation using [Demucs v4](https://github.com/facebookresearch/demucs)  
> Split any track into `vocals`, `drums`, `bass`, and `other` with GPU or CPU processing.

---

## Quick Start

```bash
git clone https://github.com/cmsolson75/StemSplitter.git
cd StemSplitter

# Build Docker images
make build

# Start the app (choose one)
make up-gpu   # NVIDIA GPU required
make up-cpu   # CPU only
````

**Example (CPU mode):**

```
$ make up-cpu
Starting (CPU)...
[+] Running 4/4
 ✔ Network stemsplittertool_default          Created  0.0s
 ✔ Volume "stemsplittertool_model_cache"     Created  0.0s
 ✔ Container stemsplittertool-backend-cpu-1  Started  0.2s
 ✔ Container stemsplittertool-frontend-1     Started  0.2s
NAME                             IMAGE                          COMMAND                  SERVICE       CREATED                  STATUS                                     PORTS
stemsplittertool-backend-cpu-1   stemsplittertool-backend-cpu   "uvicorn main:app --…"   backend-cpu   Less than a second ago   Up Less than a second (health: starting)   0.0.0.0:8000->8000/tcp
stemsplittertool-frontend-1      stemsplittertool-frontend      "docker-entrypoint.s…"   frontend      Less than a second ago   Up Less than a second                      0.0.0.0:3000->3000/tcp
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

Open [http://localhost:3000](http://localhost:3000), upload an audio file, and download the ZIP with separated stems.

**Example output:**

```
song.mp3 → song_separated.zip
├── drums.wav
├── bass.wav
├── vocals.wav
└── other.wav
```

---

## Makefile Commands

| Command       | Description                                                   |
| ------------- | ------------------------------------------------------------- |
| `make build`  | Build all Docker images                                       |
| `make up-gpu` | Start frontend + GPU backend (requires NVIDIA GPU)            |
| `make up-cpu` | Start frontend + CPU backend                                  |
| `make status` | Show running services and access URLs                         |
| `make logs`   | View container logs in real time                              |
| `make down`   | Stop all services                                             |
| `make clean`  | Remove containers, networks, volumes, and prune unused images |

> **Tip:** Uses `docker compose` by default. For the legacy plugin:
> `make COMPOSE="docker-compose" up-gpu`

---

## Requirements

**Hardware**

* **NVIDIA GPU** (GTX 1060+ recommended) for fastest processing
* **Apple Silicon** (M1/M2/M4) or **Intel/AMD CPU** (≥4 cores) supported

**Software**

* Docker ≥ 20.10
* Docker Compose plugin ≥ 2.0
* GNU Make
* Modern browser (Chrome, Firefox, Safari)

**Recommended**

* 8GB+ RAM
* 2GB+ free disk space

---

## Usage Flow

1. **Build images**

   ```bash
   make build
   ```
2. **Start services**

   ```bash
   make up-gpu  # GPU mode
   make up-cpu  # CPU mode
   ```
3. **Check status**

   ```bash
   make status
   ```
4. **Upload audio** via [http://localhost:3000](http://localhost:3000)
5. **Download results** – ZIP with `drums.wav`, `bass.wav`, `vocals.wav`, `other.wav`
6. **Stop services**

   ```bash
   make down
   ```
7. **Full cleanup**

   ```bash
   make clean
   ```

---

## Configuration

Edit `config.yml`:

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

## API Access

* **Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

Example:

```bash
curl -X POST "http://localhost:8000/separate" \
     -H "accept: application/zip" \
     -F "file=@track.mp3" \
     -o stems.zip
```

---

## Troubleshooting

| Problem             | Solution                                                                    |
| ------------------- | --------------------------------------------------------------------------- |
| `"Failed to fetch"` | Ensure backend is running on [http://localhost:8000](http://localhost:8000) |
| Processing slow     | Use GPU mode if available                                                   |
| Out of memory (OOM) | Shorter audio, lower sample rate, or increase Docker memory                 |
| Unsupported format  | Convert to WAV or MP3                                                       |
| GPU not detected    | Verify NVIDIA drivers and Docker GPU runtime                                |

**Performance tips**

* Use WAV for predictable quality
* Keep files under 10 minutes
* Close other heavy applications

---

## Contributing

1. Fork the repository
2. Create a feature branch:
   `git checkout -b feat/your-feature`
3. Commit changes:
   `git commit -m "feat: your-feature"`
4. Push to your fork:
   `git push origin feat/your-feature`
5. Open a Pull Request

---

## Additional Documentation

For service-specific details:

* [Backend README](backend/README.md)
* [Frontend README](frontend/README.md)

*Additional READMEs generated with [Skim](https://github.com/cmsolson75/skim) and GPT-5, with minor editing by author.*

---

## License

MIT — see [LICENSE](LICENSE)

---

## Acknowledgments

* [Demucs (Facebook Research)](https://github.com/facebookresearch/demucs)
* [FastAPI](https://fastapi.tiangolo.com)
* [Next.js](https://nextjs.org)
