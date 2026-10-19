#!/usr/bin/env bash
# PixelIQ Result Generator — desktop build (Linux / macOS)
# Produces: dist/PixelIQResultGenerator
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3)"
fi

echo "[build] using $PYTHON"
"$PYTHON" -m pip install -q --upgrade pyinstaller

"$PYTHON" -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name PixelIQResultGenerator \
  --paths . \
  --collect-all school_result_generator \
  --collect-all result_app \
  --collect-all django \
  --collect-all crispy_forms \
  --collect-all crispy_bootstrap5 \
  --collect-all reportlab \
  --collect-submodules openpyxl \
  --collect-submodules xlrd \
  --collect-data reportlab \
  desktop/launch.py

echo "[build] done -> dist/PixelIQResultGenerator"
