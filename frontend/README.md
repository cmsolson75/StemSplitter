# StemSplitter Frontend

Next.js UI for uploading audio and downloading separated stems. Uses shadcn/ui, Tailwind CSS, and lucide-react.

## Tech Stack

* Next.js (App Router, React 18)
* TypeScript
* Tailwind CSS
* shadcn/ui
* lucide-react

## Prerequisites

* Node.js 18+
* PNPM/Yarn/NPM (examples use `pnpm`)
* Backend API reachable at `http://localhost:8000` (default) or override via `NEXT_PUBLIC_API_URL`

## Setup

```bash
pnpm install
# or: npm install / yarn
```

Create `.env.local`:

```bash
# Defaults to http://localhost:8000 if unset
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
pnpm dev
# App at http://localhost:3000
```

> If running full stack via Makefile/Compose, start the backend first (e.g., `make up-cpu` or `make up-gpu`). Ensure CORS on the backend allows `http://localhost:3000`.

## Build & Preview

```bash
pnpm build
pnpm start
```

## UI Component

Main component (client) orchestrates upload → process → download:

* File validation:

  * Extensions: `.wav`, `.mp3`, `.aiff`, `.m4a`, `.flac`, `.ogg`
  * Max file size: 100 MB
* API call:

  * `POST {NEXT_PUBLIC_API_URL}/separate`
  * Multipart form with `file`
  * Do **not** set `Content-Type` manually; let the browser set multipart boundary.
* Response handling:

  * Expects `application/zip`
  * Generates an object URL for download
* State machine (`AppState`):

  * `upload` → `processing` → `complete` | `error`

### Public API Contract (frontend expectations)

```
POST /separate
Req: multipart/form-data, field "file" (audio)
Res: 200 application/zip (4 WAV stems zipped)
Err: JSON body { "detail": string } with appropriate HTTP status
```

## Files & Conventions

* Component: `AudioSplitter` (client component)
* Uses shadcn/ui: `Card`, `Button`, `Progress`, `Alert`, `Badge`
* Icons: lucide-react (`Upload`, `Music`, `Download`, …)
* Tailwind utility classes for layout/animations

> If you need additional shadcn/ui components:
>
> ```bash
> # Example
> pnpm dlx shadcn-ui@latest add dialog
> ```

## Configuration

* **Supported formats** and **max size** are defined in the component:

  ```ts
  const SUPPORTED_FORMATS = ['.wav', '.mp3', '.aiff', '.m4a', '.flac', '.ogg']
  const MAX_FILE_SIZE = 100 * 1024 * 1024
  ```

  Keep these in sync with backend `config.yaml` (`audio.supported_formats`, `audio.max_file_size`).

* **API base URL**:

  * `NEXT_PUBLIC_API_URL` at runtime (defaults to `http://localhost:8000` if unset)

## Error Handling

Common cases mapped to clear messages:

* Network/CORS:

  * “Failed to fetch” → “Cannot connect to server. Make sure your backend is running on [http://localhost:8000”](http://localhost:8000”)
* Backend validation:

  * Unsupported format → surface `detail` from backend
* Server errors:

  * Non-JSON errors → “Server error: <status> <statusText>”

## Accessibility

* Buttons/labels are keyboard accessible
* Drag-and-drop area supports click-to-browse
* Consider adding `aria-live` to surface processing status for screen readers if needed

## Troubleshooting

* **CORS error**: ensure backend allows `http://localhost:3000`. Backend uses FastAPI CORS; add your origin if changed.
* **413 / Payload too large**: increase backend/Docker upload limits; keep files ≤ 100 MB by default.
* **ZIP downloads but empty**: verify backend returns `application/zip` and that stems were written; check backend logs.

## Scripts

```bash
pnpm dev     # start dev server
pnpm build   # production build
pnpm start   # run production build
```

## License

MIT (see root `LICENSE`).
