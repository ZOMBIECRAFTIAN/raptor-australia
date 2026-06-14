#!/usr/bin/env bash
# One-shot environment setup on Linux/macOS.
# Usage:  ./scripts/setup.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Australian Raptor CNN environment setup"

# Detect conda
if command -v conda >/dev/null 2>&1; then
    if ! conda env list | grep -q '^raptor_env\s'; then
        echo "Creating conda env 'raptor_env' (Python 3.13)..."
        conda create -n raptor_env python=3.13 -y
    fi
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate raptor_env
else
    echo "conda not found - using a venv at ./.venv-modern instead."
    if [ ! -d .venv-modern ]; then
        python3 -m venv .venv-modern
    fi
    # shellcheck disable=SC1091
    source .venv-modern/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

echo
echo "Setup complete."
echo "  Next: ./scripts/run.sh   (and place models/best_model.pth)"
