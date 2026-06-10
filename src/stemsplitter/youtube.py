from pathlib import Path


def is_url(text) -> bool:
    t = (text or "").strip().lower()
    return t.startswith("http://") or t.startswith("https://")


def download_audio(url: str, work_dir: Path) -> tuple[Path, str]:
    """Pobiera audio z linku (YouTube itd.) do work_dir jako WAV. Wymaga yt-dlp + ffmpeg.

    Zwraca (sciezka_wav, tytul) — tytul sluzy do nazwania paczki wynikowej."""
    import yt_dlp

    work_dir = Path(work_dir)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(work_dir / "yt_%(id)s.%(ext)s"),
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    title = (info.get("title") or "").strip() or info["id"]
    return work_dir / f"yt_{info['id']}.wav", title
