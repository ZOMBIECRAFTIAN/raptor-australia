"""YOLO bird detector used before species classification.

The classifier remains EfficientNetB4. YOLO is used as the detector/cropper:
it localises birds in frames or photos, then the CNN classifies each crop
into the validated Australian raptor classes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


COCO_BIRD_CLASS_ID = 14


class YoloUnavailable(RuntimeError):
    """Raised when the optional ultralytics dependency is unavailable."""


@dataclass(frozen=True)
class BirdBox:
    bbox: list[int]
    confidence: float
    source: str = "yolo"


class YoloBirdDetector:
    """Thin wrapper around Ultralytics YOLO for COCO bird detections."""

    def __init__(self, weights: str | Path = "yolov8n.pt",
                 confidence: float = 0.5) -> None:
        try:
            from ultralytics import YOLO
        except Exception as exc:  # pragma: no cover - optional dependency
            raise YoloUnavailable(
                "Install ultralytics and provide YOLO weights to enable "
                "YOLO bird detection."
            ) from exc

        self.weights = str(weights)
        self.confidence = confidence
        self.model = YOLO(self.weights)

    def detect(self, image: Any) -> list[BirdBox]:
        """Return COCO bird boxes as integer xyxy boxes."""
        results = self.model.predict(
            source=image,
            classes=[COCO_BIRD_CLASS_ID],
            conf=self.confidence,
            verbose=False,
        )
        if not results:
            return []

        boxes = getattr(results[0], "boxes", None)
        if boxes is None or len(boxes) == 0:
            return []

        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        cls = boxes.cls.cpu().numpy()

        out: list[BirdBox] = []
        for coords, score, cls_id in zip(xyxy, conf, cls):
            if int(cls_id) != COCO_BIRD_CLASS_ID:
                continue
            x0, y0, x1, y1 = [int(round(float(v))) for v in coords]
            out.append(BirdBox(
                bbox=[x0, y0, x1, y1],
                confidence=round(float(score), 3),
            ))
        return out
