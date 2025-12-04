from dataclasses import dataclass, field
from typing import Dict, List, Optional

import cv2
import numpy as np
from sklearn.cluster import KMeans

from src.models.tracker import TrackState


@dataclass
class TeamColorClassifier:
    """Clusters jersey colors to assign team IDs."""

    n_clusters: int = 2
    max_samples: int = 200
    _samples: List[np.ndarray] = field(default_factory=list)
    _model: Optional[KMeans] = None
    _track_team_map: Dict[int, int] = field(default_factory=dict)

    def _extract_jersey_color(self, frame: np.ndarray, track: TrackState) -> Optional[np.ndarray]:
        x1, y1, x2, y2 = track.bbox_xyxy.astype(int)
        y_mid = y1 + int((y2 - y1) * 0.4)
        jersey_crop = frame[y1:y_mid, x1:x2]
        if jersey_crop.size == 0:
            return None
        lab = cv2.cvtColor(jersey_crop, cv2.COLOR_BGR2LAB)
        mean_color = lab.reshape(-1, 3).mean(axis=0)
        return mean_color

    def add_samples(self, frame: np.ndarray, tracks: List[TrackState]) -> None:
        if self._model is not None:
            return
        for track in tracks:
            if track.class_id not in (0, 1):  # assume COCO person classes
                continue
            color = self._extract_jersey_color(frame, track)
            if color is not None:
                self._samples.append(color)
        if len(self._samples) >= self.max_samples:
            self.fit()

    def fit(self) -> None:
        if not self._samples:
            raise RuntimeError("No samples collected for K-Means.")
        data = np.vstack(self._samples)
        self._model = KMeans(n_clusters=self.n_clusters, n_init=10)
        self._model.fit(data)

    def predict(self, frame: np.ndarray, track: TrackState) -> Optional[int]:
        if self._model is None:
            return None
        if track.class_id not in (0, 1):
            return None
        color = self._extract_jersey_color(frame, track)
        if color is None:
            return None
        team_id = int(self._model.predict(color.reshape(1, -1))[0])
        self._track_team_map[track.track_id] = team_id
        return team_id

    def get_team(self, track_id: int) -> Optional[int]:
        return self._track_team_map.get(track_id)
