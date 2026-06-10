"""Sprawdzanie nowej wersji na GitHubie i start aktualizacji.

Kazdy blad sieci/pliku = cicha rezygnacja (None) — brak internetu nie moze
psuc startu aplikacji.
"""

import os
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

_RAW_VERSION_URL = "https://raw.githubusercontent.com/lysy1033/Stem-Splitter/main/VERSION"


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def current_version() -> str:
    try:
        return (_root() / "VERSION").read_text(encoding="utf-8").strip() or "0"
    except OSError:
        return "0"  # stara kopia bez pliku VERSION


def latest_version(timeout: float = 3.0) -> str | None:
    try:
        # parametr ts omija cache CDN (raw.githubusercontent trzyma plik do ~5 min)
        url = f"{_RAW_VERSION_URL}?ts={int(time.time())}"
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8").strip() or None
    except Exception:
        return None


def _as_tuple(version: str) -> tuple[int, ...]:
    parts = []
    for p in version.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    return _as_tuple(latest) > _as_tuple(current)


def update_available() -> tuple[str, str] | None:
    """(biezaca, najnowsza) jesli jest nowsza wersja, inaczej None."""
    current = current_version()
    latest = latest_version()
    if latest is not None and is_newer(latest, current):
        return (current, latest)
    return None


def _updater_script() -> Path:
    name = "update-windows.bat" if sys.platform == "win32" else "update-mac.command"
    return _root() / "installers" / name


def start_update() -> None:
    """Odpala skrypt aktualizujacy jako osobny proces i zamyka aplikacje."""
    script = _updater_script()
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", "", str(script)])
    else:
        subprocess.Popen(["open", str(script)])
    # 1.5 s: Gradio musi zdazyc oddac odpowiedz do przegladarki przed zamknieciem
    timer = threading.Timer(1.5, lambda: os._exit(0))
    timer.daemon = True  # nie blokuje wyjscia procesu (np. w testach)
    timer.start()
