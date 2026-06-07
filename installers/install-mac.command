#!/bin/bash
# StemSplitter — instalator macOS / macOS installer
set -e
cd "$(dirname "$0")/.."

echo ""
echo "=================================================="
echo "   StemSplitter — instalacja / installation"
echo "=================================================="
echo ""
echo "Potrwa kilka minut. Nie zamykaj tego okna."
echo "This takes a few minutes. Do not close this window."
echo ""

# [1/3] narzedzia / tools (uv — pobierane jako binarka, bez Xcode/Homebrew)
if ! command -v uv >/dev/null 2>&1; then
  echo "[1/3] Instaluje narzedzia... / Installing tools..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

# [2/3] srodowisko + WSZYSTKIE zaleznosci (w tym ffmpeg przez pakiet pip 'static-ffmpeg')
# w widocznym folderze ~/StemSplitter (poza OneDrive). Brak Homebrew/Xcode.
echo "[2/3] Pobieram aplikacje (najdluzszy krok)... / Downloading the app (longest step)..."
VENV="$HOME/StemSplitter/venv"
uv venv "$VENV" --python 3.11
# wariant akceleracji (Apple Silicon: cpu == CoreML)
uv pip install --python "$VENV" "audio-separator[cpu]"
# reszta zaleznosci z definicji projektu (pyproject.toml: gradio, pyyaml, yt-dlp, static-ffmpeg)
uv pip install --python "$VENV" -e .

# [3/3] odblokuj skrypty, by uruchamialy sie bez ostrzezenia systemu
echo "[3/3] Konczę... / Finishing..."
xattr -dr com.apple.quarantine "$(dirname "$0")" 2>/dev/null || true

echo ""
echo "=================================================="
echo "   GOTOWE! / DONE!"
echo "   Wyniki znajdziesz w: $HOME/StemSplitter/output"
echo "   Your results will be in: $HOME/StemSplitter/output"
echo "   Aby uruchomic ponownie kliknij: run-mac.command"
echo "   To run again, double-click: run-mac.command"
echo "=================================================="
echo ""
echo "Uruchamiam StemSplitter... / Starting StemSplitter..."
PYTHONPATH=src "$VENV/bin/python" -m stemsplitter.app
