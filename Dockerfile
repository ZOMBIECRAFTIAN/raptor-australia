# ────────────────────────────────────────────────────────
# Australian Raptor CNN + AUSLAN — Container image
# ────────────────────────────────────────────────────────
# Build:    docker build -t raptor-au .
# Run:      docker run -p 5000:5000 \
#               -v "$(pwd)/models:/app/models:ro" \
#               raptor-au
#
# Model weights (models/best_model.pth) and optional YOLO weights
# (models/yolov8n.pt) are expected to be mounted at runtime. They
# are excluded from this image to keep it small and to respect
# GitHub's file-size limits. Train via notebooks/retrain.py.
# ────────────────────────────────────────────────────────

FROM python:3.13-slim

WORKDIR /app

# System libraries that Pillow / torchvision need to load JPEG/PNG
RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libfreetype6 \
        libgl1 \
        libglib2.0-0 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python deps — installed first so Docker caches the layer.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Application code
COPY gui ./gui
COPY notebooks ./notebooks
COPY results ./results
COPY docs ./docs
COPY README.md LICENSE CHANGELOG.md CITATION.cff ./

# Non-root user
RUN useradd --create-home --uid 1000 app && \
    mkdir -p /app/models /app/dataset /app/gui/uploads && \
    chown -R app /app
USER app

# Flask listens on 5000
EXPOSE 5000
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=gui.app \
    FLASK_RUN_HOST=0.0.0.0

WORKDIR /app/gui

# Production server (gunicorn). Override CMD with `python app.py`
# during development to keep Flask's debug auto-reloader.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "2", "--threads", "4", "--timeout", "120", \
     "app:app"]
