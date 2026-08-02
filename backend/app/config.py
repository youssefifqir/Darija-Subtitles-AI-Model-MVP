import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
JOBS_DIR = DATA_DIR / "jobs"
CORRECTIONS_LOG = DATA_DIR / "corrections.jsonl"

for d in (UPLOADS_DIR, JOBS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# "cpu", "cuda", or "mps". CUDA needs ~4GB+ VRAM free; fall back to cpu if it OOMs.
ASR_DEVICE = os.environ.get("ASR_DEVICE", "cuda")
# Swap via env var to compare checkpoints, e.g.:
#   ychafiqui/whisper-small-darija
#   Anass-Srk/fine-tuned-whisper-small-darija
ASR_MODEL_ID = os.environ.get("ASR_MODEL_ID", "ychafiqui/whisper-small-darija")

# VAD tuning
VAD_MIN_SPEECH_MS = 250
VAD_MIN_SILENCE_MS = 300
VAD_SPEECH_PAD_MS = 200

# Merge adjacent VAD segments closer than this into one ASR call (fewer, more natural subtitle lines)
VAD_MERGE_GAP_S = 0.5
VAD_MAX_SEGMENT_S = 12.0
