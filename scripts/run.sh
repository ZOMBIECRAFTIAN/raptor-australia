#!/usr/bin/env bash
# Quick launcher for the Flask web app on Linux/macOS.
# Usage:  ./scripts/run.sh
set -euo pipefail

cd "$(dirname "$0")/../gui"

if [ ! -f ../models/best_model.pth ]; then
    echo "✗  Model weights not found at models/best_model.pth"
    echo "   Train the model via notebooks/03_training.ipynb first,"
    echo "   or place a pre-trained .pth file at that path."
    exit 1
fi

echo "🦅  Starting Australian Raptor CNN on http://localhost:5000"
exec python app.py
