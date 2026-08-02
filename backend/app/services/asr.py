from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile as sf

from app.config import ASR_DEVICE, ASR_MODEL_ID

SAMPLE_RATE = 16000


@lru_cache(maxsize=1)
def _get_pipeline():
    import torch
    from transformers import pipeline

    device = 0 if ASR_DEVICE == "cuda" else -1
    dtype = torch.float16 if ASR_DEVICE == "cuda" else torch.float32
    return pipeline(
        "automatic-speech-recognition",
        model=ASR_MODEL_ID,
        device=device,
        torch_dtype=dtype,
    )


def load_wav_mono16k(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != SAMPLE_RATE:
        raise ValueError(f"Expected {SAMPLE_RATE}Hz audio, got {sr}Hz — extract via ffmpeg first")
    return data


def transcribe_segment(wav: np.ndarray, start_s: float, end_s: float) -> str:
    pipe = _get_pipeline()
    start_i = max(0, int(start_s * SAMPLE_RATE))
    end_i = min(len(wav), int(end_s * SAMPLE_RATE))
    chunk = wav[start_i:end_i]
    if chunk.size == 0:
        return ""

    result = pipe(
        {"array": chunk, "sampling_rate": SAMPLE_RATE},
        generate_kwargs={"language": "arabic", "task": "transcribe"},
    )
    return result["text"].strip()
