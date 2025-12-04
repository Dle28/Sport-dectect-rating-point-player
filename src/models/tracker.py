from dataclasses import dataclass
from typing import List

import numpy as np
from supervision import Detections
from supervision.tracker.byte_tracker import ByteTrack, ByteTrackArgs

from src.config import TrackingConfig


@dataclass
class TrackState:
    track_id: int
    bbox_xyxy: np.ndarray  # shape: (4,)
    score: float
    class_id: int


class ByteTrackerWrapper:
    """ByteTrack wrapper returning simple track states."""

    def __init__(self, config: TrackingConfig):
        self.config = config
        args = ByteTrackArgs(
            track_thresh=config.track_thresh,
            match_thresh=config.match_thresh,
            track_buffer=config.track_buffer,
            mot20=config.mot20,
        )
        self.tracker = ByteTrack(args=args)

    def update(self, detections: Detections) -> List[TrackState]:
        tracks = self.tracker.update_with_detections(detections)
        track_states: List[TrackState] = []
        for track in tracks:
            track_id = getattr(track, "id", getattr(track, "track_id", None))
            if track_id is None:
                continue
            track_states.append(
                TrackState(
                    track_id=int(track_id),
                    bbox_xyxy=getattr(track, "xyxy", np.array([0, 0, 0, 0], dtype=float)),
                    score=float(getattr(track, "score", getattr(track, "confidence", 0.0))),
                    class_id=int(getattr(track, "class_id", -1)),
                )
            )
        return track_states

    @staticmethod
    def convert_detections(
        xyxy: np.ndarray, confidence: np.ndarray, class_id: np.ndarray
    ) -> Detections:
        """Create a supervision.Detections object from arrays."""
        return Detections(
            xyxy=xyxy.astype(float),
            confidence=confidence.astype(float),
            class_id=class_id.astype(int),
        )
