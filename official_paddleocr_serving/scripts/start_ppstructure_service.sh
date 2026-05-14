#!/usr/bin/env bash
set -euo pipefail

# Official PaddleX serving demo for PP-StructureV3.
# If your installed PaddleX reports a different pipeline name, set:
#   PADDLEX_PIPELINE=<official-name-or-yaml-path> bash scripts/start_ppstructure_service.sh

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8081}"
PIPELINE="${PADDLEX_PIPELINE:-PP-StructureV3}"

echo "Starting official PaddleX PP-StructureV3 service on ${HOST}:${PORT}"
echo "Pipeline: ${PIPELINE}"
echo "If startup fails because the pipeline name is unknown, export the official PaddleX pipeline config to YAML and set PADDLEX_PIPELINE to that YAML path."

paddlex --serve --pipeline "${PIPELINE}" --host "${HOST}" --port "${PORT}"
