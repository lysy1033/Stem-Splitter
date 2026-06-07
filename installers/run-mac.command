#!/bin/bash
# StemSplitter — uruchomienie / launch (macOS)
set -e
cd "$(dirname "$0")/.."
VENV="$HOME/StemSplitter/venv"
if [ ! -x "$VENV/bin/python" ]; then
  echo "Najpierw uruchom install-mac.command / Run install-mac.command first."
  read -p "Enter..."
  exit 1
fi
echo "Uruchamiam StemSplitter... / Starting StemSplitter..."
PYTHONPATH=src "$VENV/bin/python" -m stemsplitter.app
