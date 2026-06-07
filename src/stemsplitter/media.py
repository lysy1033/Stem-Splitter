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
