#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "== Instalacja StemSplitter (macOS) =="

if ! command -v uv >/dev/null 2>&1; then
  echo "Instaluje uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Instaluje ffmpeg (Homebrew)..."
  if ! command -v brew >/dev/null 2>&1; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  brew install ffmpeg
fi

VENV="$HOME/.stem-splitter/venv"
uv venv "$VENV" --python 3.11
# Apple Silicon: wariant cpu zawiera CoreML
uv pip install --python "$VENV" "audio-separator[cpu]" gradio pyyaml yt-dlp
echo "Gotowe. Uruchom przez run-mac.command"
read -p "Nacisnij Enter, aby zamknac."
