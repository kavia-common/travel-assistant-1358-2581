#!/usr/bin/env bash
set -euo pipefail

# Attempt to find flake8 on PATH. If not found, provide a helpful message.
if ! command -v flake8 >/dev/null 2>&1; then
  echo "flake8 is not installed or not on PATH."
  echo "Install it with: pip install flake8"
  exit 1
fi

# Run flake8 with local configuration
flake8 .
