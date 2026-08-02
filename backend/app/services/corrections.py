import json
import threading
from datetime import datetime, timezone

from app.config import CORRECTIONS_LOG

_LOCK = threading.Lock()


def log_correction(job_id: str, segment_id: int, original_text: str, corrected_text: str) -> None:
    """F6: log every manual correction as future fine-tuning data."""
    if original_text == corrected_text:
        return
    entry = {
        "job_id": job_id,
        "segment_id": segment_id,
        "original_text": original_text,
        "corrected_text": corrected_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _LOCK:
        with open(CORRECTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
