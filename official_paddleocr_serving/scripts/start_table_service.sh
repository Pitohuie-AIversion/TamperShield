#!/usr/bin/env bash
set -euo pipefail

# Official PaddleX serving demo for Table Recognition v2.
# The PaddleOCR CLI name is table_recognition_v2, but the PaddleX serving
# pipeline name can vary by installed PaddleX/PaddleOCR version. Do not guess:
# set PADDLEX_PIPELINE to the official pipeline name or to an exported YAML config.

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8082}"
PIPELINE="${PADDLEX_PIPELINE:-}"

if [[ -z "${PIPELINE}" ]]; then
  echo "PADDLEX_PIPELINE is required for Table Recognition v2 serving."
  echo "Confirm the official PaddleX pipeline name or export a pipeline YAML, then run:"
  echo "  PADDLEX_PIPELINE=<official-name-or-yaml-path> bash scripts/start_table_service.sh"
  exit 2
fi

echo "Starting official PaddleX Table Recognition v2 service on ${HOST}:${PORT}"
echo "Pipeline: ${PIPELINE}"

paddlex --serve --pipeline "${PIPELINE}" --host "${HOST}" --port "${PORT}"
