#!/usr/bin/env bash
set -euo pipefail

# One-click environment deployment for the official PaddleOCR/PaddleX demo.
# This script installs dependencies only. It does not start long-running services.

ENV_NAME="${ENV_NAME:-paddleocr_official}"
PYTHON_VERSION="${PYTHON_VERSION:-3.10}"
SKIP_CONDA_CREATE="${SKIP_CONDA_CREATE:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REQUIREMENTS="${PROJECT_DIR}/requirements_official.txt"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda was not found in PATH. Please install Anaconda/Miniconda first." >&2
  exit 1
fi

if [[ ! -f "${REQUIREMENTS}" ]]; then
  echo "requirements_official.txt not found: ${REQUIREMENTS}" >&2
  exit 1
fi

cd "${PROJECT_DIR}"

echo "Official PaddleOCR serving deployment"
echo "Project directory: ${PROJECT_DIR}"
echo "Conda environment: ${ENV_NAME}"
echo "Python version: ${PYTHON_VERSION}"

if conda env list | awk '{print $1}' | grep -Fxq "${ENV_NAME}"; then
  echo "Conda environment already exists, reusing: ${ENV_NAME}"
elif [[ "${SKIP_CONDA_CREATE}" == "1" ]]; then
  echo "Skipping conda environment creation because SKIP_CONDA_CREATE=1."
else
  echo "Creating conda environment: ${ENV_NAME}"
  conda create -n "${ENV_NAME}" "python=${PYTHON_VERSION}" -y
fi

echo "Installing Python dependencies..."
conda run -n "${ENV_NAME}" python -m pip install -r "${REQUIREMENTS}"

echo "Installing PaddleX serving plugin..."
conda run -n "${ENV_NAME}" paddlex --install serving -y

echo "Running environment check..."
conda run -n "${ENV_NAME}" python scripts/check_environment.py

echo ""
echo "Deployment completed."
echo "Next commands:"
echo "  conda activate ${ENV_NAME}"
echo "  bash scripts/start_ocr_service.sh"
echo "  bash scripts/start_ppstructure_service.sh"
echo "  PADDLEX_PIPELINE=table_recognition_v2 bash scripts/start_table_service.sh"
