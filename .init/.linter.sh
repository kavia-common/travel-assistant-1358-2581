#!/bin/bash
set -euo pipefail

# Move to the frontend service directory
cd /home/kavia/workspace/code-generation/travel-assistant-1358-2581/ClothingRecommendationService

# Ensure flake8 is available; install if missing.
if ! command -v flake8 >/dev/null 2>&1; then
  echo "flake8 not found on PATH. Attempting to install..."
  python3 -m pip install --quiet --no-input flake8 || pip install --quiet --no-input flake8
fi

# Run flake8 using the local configuration
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  echo "Linting failed with exit code ${LINT_EXIT_CODE}"
  exit 1
fi
echo "Linting passed."
