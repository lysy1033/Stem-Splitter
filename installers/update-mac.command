#!/bin/bash
# StemSplitter — aktualizacja / update (macOS)
# Cala logika w funkcji: bash wczytuje ja w calosci PRZED wykonaniem, wiec
# nadpisanie tego pliku w kroku [2/3] nie psuje trwajacego skryptu.
main() {
  set -e
  cd "$(dirname "$0")/.."
  APP_DIR="$(pwd)"

  echo ""
  echo "=================================================="
  echo "   StemSplitter — aktualizacja / update"
  echo "=================================================="
  echo ""
  sleep 2  # czas na zamkniecie aplikacji, gdy start z przycisku w aplikacji

  VENV="$HOME/StemSplitter/venv"
  if [ ! -x "$VENV/bin/python" ]; then
    echo "Najpierw uruchom install-mac.command / Run install-mac.command first."
    read -p "Enter..."
    exit 1
  fi

  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT

  echo "[1/3] Pobieram nowa wersje... / Downloading the new version..."
  curl -L -o "$TMP/app.zip" "https://github.com/lysy1033/Stem-Splitter/archive/refs/heads/main.zip"
  unzip -q "$TMP/app.zip" -d "$TMP"

  echo "[2/3] Podmieniam pliki aplikacji... / Replacing app files..."
  cp -R "$TMP/Stem-Splitter-main/." "$APP_DIR/"

  echo "[3/3] Aktualizuje zaleznosci... / Updating dependencies..."
  export PATH="$HOME/.local/bin:$PATH"
  uv pip install --python "$VENV" "audio-separator[cpu]"
  uv pip install --python "$VENV" -e .
  xattr -dr com.apple.quarantine "$APP_DIR/installers" 2>/dev/null || true

  echo ""
  echo "Gotowe! Uruchamiam StemSplitter... / Done! Starting StemSplitter..."
  cd "$APP_DIR"
  export PYTHONPATH=src
  trap - EXIT
  rm -rf "$TMP"  # exec zastepuje proces, trap EXIT by nie odpalil
  exec "$VENV/bin/python" -m stemsplitter.app
}
main "$@"
