from pathlib import Path
from functools import lru_cache

from app.config import (
    VAD_MIN_SPEECH_MS,
    VAD_MIN_SILENCE_MS,
    VAD_SPEECH_PAD_MS,
    VAD_MERGE_GAP_S,
    VAD_MAX_SEGMENT_S,
)


@lru_cache(maxsize=1)
def _get_vad_model():
    from silero_vad import load_silero_vad
    return load_silero_vad()


def get_speech_segments(wav_path: Path) -> list[tuple[float, float]]:
    """Run Silero VAD on a 16kHz mono WAV file. Returns merged (start, end) second tuples."""
    from silero_vad import read_audio, get_speech_timestamps

    model = _get_vad_model()
    wav = read_audio(str(wav_path), sampling_rate=16000)

    raw = get_speech_timestamps(
        wav,
        model,
        sampling_rate=16000,
        min_speech_duration_ms=VAD_MIN_SPEECH_MS,
        min_silence_duration_ms=VAD_MIN_SILENCE_MS,
        speech_pad_ms=VAD_SPEECH_PAD_MS,
        return_seconds=True,
    )

    if not raw:
        return []

    merged: list[tuple[float, float]] = []
    cur_start, cur_end = raw[0]["start"], raw[0]["end"]

    for seg in raw[1:]:
        gap = seg["start"] - cur_end
        would_be_len = seg["end"] - cur_start
        if gap <= VAD_MERGE_GAP_S and would_be_len <= VAD_MAX_SEGMENT_S:
            cur_end = seg["end"]
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = seg["start"], seg["end"]
    merged.append((cur_start, cur_end))

    # Split any segment still longer than the cap into fixed-size chunks
    final: list[tuple[float, float]] = []
    for start, end in merged:
        length = end - start
        if length <= VAD_MAX_SEGMENT_S:
            final.append((start, end))
            continue
        n_chunks = int(length // VAD_MAX_SEGMENT_S) + 1
        chunk_len = length / n_chunks
        for i in range(n_chunks):
            final.append((start + i * chunk_len, start + (i + 1) * chunk_len))

    return final
