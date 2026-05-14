#!/usr/bin/env bash
set -euo pipefail

# Official PaddleX serving demo for the PaddleOCR OCR pipeline.
# Install serving support first:
#   paddlex --install serving

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
PIPELINE="${PADDLEX_PIPELINE:-OCR}"

echo "Starting official PaddleX OCR service on ${HOST}:${PORT}"
echo "Pipeline: ${PIPELINE}"

paddlex --serve --pipeline "${PIPELINE}" --host "${HOST}" --port "${PORT}"
