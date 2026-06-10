import re
import subprocess
from pathlib import Path

AUDIO_EXT = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


class UnsupportedFormatError(ValueError):
    pass


def prepare_input(src: Path, work_dir: Path) -> Path:
    src = Path(src)
    ext = src.suffix.lower()
    if ext in AUDIO_EXT:
        return src
    if ext in VIDEO_EXT:
        return _extract_audio(src, work_dir)
    raise UnsupportedFormatError(
        f"Nieobslugiwany format: {ext}. Uzyj MP3 lub MP4."
    )


def _extract_audio(src: Path, work_dir: Path) -> Path:
    out = Path(work_dir) / (src.stem + ".wav")
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


_ILLEGAL_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_filename(name: str, fallback: str = "utwor") -> str:
    """Tytul utworu -> bezpieczna nazwa pliku (Windows/macOS), max 80 znakow."""
    cleaned = _ILLEGAL_FILENAME.sub("", str(name))
    cleaned = re.sub(r"\s+", " ", cleaned).strip().strip(".")
    return cleaned[:80] or fallback


def to_mp3(src: Path, out_dir: Path, title: str) -> Path:
    """Konwertuje audio do MP3 320k (np. caly utwor z YouTube do paczki)."""
    out = Path(out_dir) / f"{safe_filename(title)}.mp3"
    cmd = ["ffmpeg", "-y", "-i", str(src),
           "-vn", "-codec:a", "libmp3lame", "-b:a", "320k", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    return out
