# Darija Subtitles — Local Demo

Minimal end-to-end slice of the MVP (see `darija_subtitles_mvp_prd.md`): upload/URL → VAD → moulsot.v0.3 ASR → segment review/edit → SRT/VTT/TXT export. Corrections are logged to `backend/data/corrections.jsonl` (F6).

Built for **local demo/testing only** — in-memory job store (resets on restart), no auth, CORS wide open. Not production config.

## Prerequisites

- Python 3.10+
- Node 18+
- **ffmpeg** on PATH — Windows: `winget install ffmpeg` (or download from ffmpeg.org and add `bin/` to PATH). Verify with `ffmpeg -version`.

## Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

### Device config

Model defaults to CPU (`ASR_DEVICE=cpu`), safest for a 4GB VRAM card since `qwen-asr` pulls in `vllm` which can be finicky on small GPUs. To try GPU:

```bash
set ASR_DEVICE=cuda        # Windows cmd
uvicorn app.main:app --reload --port 8000
```

If it OOMs or fails to init on `cuda`, fall back to `cpu` — slower per clip but fine for demo purposes (single request at a time, no concurrent users).

**Known risk:** `qwen-asr`'s dependency on `vllm==0.14.0` is a heavy install and may need adjusting (e.g. `pip install qwen-asr --no-deps` + manually installing lighter deps) if it fails to build on your machine. If that happens, share the actual pip error and we'll adapt the requirements.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Opens on `http://localhost:5173`, proxies `/api/*` to the backend on port 8000 (see `vite.config.ts`).

## Using it

1. Start backend (`uvicorn`, port 8000), then frontend (`npm run dev`, port 5173)
2. Open `http://localhost:5173`
3. Upload a file (or paste a YouTube/TikTok/Instagram URL)
4. Wait on the review page — it polls job status every 1.5s
5. Once done: click a subtitle line to jump the video there, edit text inline (saves on blur, logged as a correction if changed)
6. Export SRT/VTT/TXT from the buttons above the segment list

## What's stubbed / simplified vs. the full PRD

- No accounts/usage metering (F8) — out of scope for a demo
- Job store is in-memory (`backend/app/services/jobs.py`) — fine for local testing, needs a real DB + queue (Celery/RQ + Redis or similar) before any real deployment
- Single-worker executor — jobs process one at a time, matches single local GPU/CPU
- No burned-in captions, diarization, dual-language export — all correctly deferred per PRD section 6
