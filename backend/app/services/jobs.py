import threading
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from app.config import UPLOADS_DIR
from app.schemas import JobDetail, Segment
from app.services import media, vad, asr
from app.services.corrections import log_correction

_JOBS: dict[str, JobDetail] = {}
_LOCK = threading.Lock()

# Single worker: one shared GPU/CPU model instance, process jobs one at a time.
_EXECUTOR = ThreadPoolExecutor(max_workers=1)


def create_job(media_filename: str) -> str:
    job_id = uuid.uuid4().hex[:12]
    with _LOCK:
        _JOBS[job_id] = JobDetail(id=job_id, status="queued", media_filename=media_filename)
    return job_id


def get_job(job_id: str) -> JobDetail | None:
    with _LOCK:
        return _JOBS.get(job_id)


def _set(job_id: str, **fields):
    with _LOCK:
        job = _JOBS[job_id]
        for k, v in fields.items():
            setattr(job, k, v)


def submit(job_id: str, source_path: Path) -> None:
    _EXECUTOR.submit(_run_pipeline, job_id, source_path)


def _run_pipeline(job_id: str, source_path: Path) -> None:
    try:
        _set(job_id, status="processing", progress="extracting audio")
        wav_path = UPLOADS_DIR / f"{job_id}.wav"
        media.extract_audio_wav(source_path, wav_path)

        _set(job_id, progress="detecting speech segments")
        spans = vad.get_speech_segments(wav_path)

        if not spans:
            _set(job_id, status="done", progress="no speech detected", segments=[])
            return

        wav = asr.load_wav_mono16k(wav_path)

        segments: list[Segment] = []
        for i, (start, end) in enumerate(spans):
            _set(job_id, progress=f"transcribing segment {i + 1}/{len(spans)}")
            text = asr.transcribe_segment(wav, start, end)
            segments.append(Segment(id=i, start=start, end=end, text=text))
            _set(job_id, segments=list(segments))

        _set(job_id, status="done", progress="done")
    except Exception as e:  # noqa: BLE001 — surface any pipeline failure to the client
        _set(job_id, status="error", error=str(e))


def update_segment_text(job_id: str, seg_id: int, new_text: str) -> Segment | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        if not job:
            return None
        for seg in job.segments:
            if seg.id == seg_id:
                original = seg.text
                seg.text = new_text
                seg.edited = True
                log_correction(job_id, seg_id, original, new_text)
                return seg
    return None
