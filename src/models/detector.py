from dataclasses import dataclass
from typing import Dict

import numpy as np
from ultralytics import YOLO

from src.config import DetectionConfig


@dataclass
class DetectionOutput:
    """Container for detection results."""

    xyxy: np.ndarray  # shape: (N, 4)
    confidence: np.ndarray  # shape: (N,)
    class_id: np.ndarray  # shape: (N,)


class YOLODetector:
    """Thin wrapper around ultralytics YOLOv8."""

    def __init__(self, config: DetectionConfig):
        self.config = config
        self.model = YOLO(config.model_path)
        self.class_map: Dict[str, int] = config.class_map

    def detect(self, frame: np.ndarray) -> DetectionOutput:
        results = self.model.predict(
            frame,
            verbose=False,
            device=self.config.device,
            conf=self.config.conf_threshold,
            iou=self.config.iou_threshold,
        )[0]

        boxes = results.boxes.xyxy.cpu().numpy()
        conf = results.boxes.conf.cpu().numpy()
        cls = results.boxes.cls.cpu().numpy().astype(int)

        mask = np.isin(cls, list(self.class_map.values()))
        return DetectionOutput(
            xyxy=boxes[mask],
            confidence=conf[mask],
            class_id=cls[mask],
        )
