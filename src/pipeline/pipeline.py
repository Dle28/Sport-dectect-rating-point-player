import json
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from supervision import Detections

from src.config import PipelineConfig
from src.models.detector import YOLODetector
from src.models.tracker import ByteTrackerWrapper, TrackState
from src.pipeline.homography import HomographyMapper
from src.pipeline.kmeans_team_classifier import TeamColorClassifier
from src.pipeline.metrics import MetricsAccumulator


class SoccerAnalyticsPipeline:
    """End-to-end pipeline for detection, tracking, and physical metrics."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.detector = YOLODetector(self.config.detection)
        self.tracker = ByteTrackerWrapper(self.config.tracking)
        self.homography = HomographyMapper(self.config.homography)
        self.team_classifier = TeamColorClassifier()
        self.metrics = MetricsAccumulator()
        self.config.paths.output_dir.mkdir(parents=True, exist_ok=True)
        self.homography.set_from_config()

    def _detections_to_supervision(self, detections) -> Detections:
        return ByteTrackerWrapper.convert_detections(
            xyxy=detections.xyxy,
            confidence=detections.confidence,
            class_id=detections.class_id,
        )

    def process_frame(self, frame_bgr: np.ndarray, timestamp_s: float) -> List[TrackState]:
        detections = self.detector.detect(frame_bgr)
        sv_detections = self._detections_to_supervision(detections)
        tracked = self.tracker.update(sv_detections)

        # bootstrap team clustering
        self.team_classifier.add_samples(frame_bgr, tracked)

        processed_tracks: List[TrackState] = []
        for track in tracked:
            center_px = self._bbox_center(track.bbox_xyxy)
            pitch_xy = self._map_to_pitch(center_px)
            team_id = self.team_classifier.predict(frame_bgr, track)
            self.metrics.update(track.track_id, pitch_xy, timestamp_s, team_id=team_id)

            annotated_track = TrackState(
                track_id=track.track_id,
                bbox_xyxy=track.bbox_xyxy,
                score=track.score,
                class_id=track.class_id,
            )
            processed_tracks.append(annotated_track)

        return processed_tracks

    def _bbox_center(self, bbox_xyxy: np.ndarray) -> tuple:
        x1, y1, x2, y2 = bbox_xyxy
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def _map_to_pitch(self, point: tuple) -> tuple:
        if self.homography.matrix is None:
            # fallback: use pixel coords as-is until homography is set
            return point
        return self.homography.image_to_pitch(point)

    def save_metrics(self, path: Optional[Path] = None) -> Path:
        output_path = path or self.config.paths.metrics_json
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(self.metrics.to_json_serializable(), f, indent=2)
        return output_path


def annotate_frame(frame_bgr: np.ndarray, tracks: List[TrackState], font_scale: float = 0.5) -> np.ndarray:
    """Simple visualization helper."""
    vis = frame_bgr.copy()
    for track in tracks:
        x1, y1, x2, y2 = track.bbox_xyxy.astype(int)
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            vis,
            f"ID {track.track_id}",
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
    return vis
