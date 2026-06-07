#!/bin/bash
set -e
cd "$(dirname "$0")/.."
VENV="$HOME/.stem-splitter/venv"
PYTHONPATH=src "$VENV/bin/python" -m stemsplitter.app
