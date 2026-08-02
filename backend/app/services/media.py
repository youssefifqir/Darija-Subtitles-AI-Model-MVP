import subprocess
from pathlib import Path


class MediaError(Exception):
    pass


def extract_audio_wav(input_path: Path, output_path: Path) -> None:
    """Extract mono 16kHz WAV from any video/audio file via ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-ar", "16000",
        "-ac", "1",
        "-vn",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise MediaError(f"ffmpeg failed: {result.stderr[-2000:]}")


def download_from_url(url: str, dest_dir: Path, job_id: str) -> Path:
    """Download audio from a YouTube/TikTok/Instagram URL via yt-dlp. Returns path to downloaded file."""
    import yt_dlp

    out_template = str(dest_dir / f"{job_id}_source.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    path = Path(filename)
    if not path.exists():
        raise MediaError(f"yt-dlp reported success but file not found: {filename}")
    return path
