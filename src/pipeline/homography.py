from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.config import HomographyConfig


@dataclass
class HomographyMapper:
    """Maps between image coordinates and top-down pitch coordinates."""

    config: HomographyConfig
    matrix: Optional[np.ndarray] = None
    inverse_matrix: Optional[np.ndarray] = None

    def compute(self, src_points: List[Tuple[float, float]], dst_points: List[Tuple[float, float]]) -> None:
        if len(src_points) != 4 or len(dst_points) != 4:
            raise ValueError("Exactly 4 source and 4 destination points are required.")
        src = np.array(src_points, dtype=np.float32)
        dst = np.array(dst_points, dtype=np.float32)
        self.matrix, _ = cv2.findHomography(src, dst)
        if self.matrix is None:
            raise RuntimeError("Failed to compute homography matrix.")
        self.inverse_matrix = np.linalg.inv(self.matrix)

    def set_from_config(self) -> None:
        if self.config.reference_points_src and self.config.reference_points_dst:
            self.compute(self.config.reference_points_src, self.config.reference_points_dst)

    def image_to_pitch(self, point_xy: Tuple[float, float]) -> Tuple[float, float]:
        if self.matrix is None:
            raise RuntimeError("Homography matrix not computed.")
        src_pt = np.array([[point_xy[0], point_xy[1], 1.0]], dtype=np.float32).T
        dst_pt = self.matrix @ src_pt
        dst_pt /= dst_pt[2]
        return float(dst_pt[0]), float(dst_pt[1])

    def pitch_to_image(self, point_xy: Tuple[float, float]) -> Tuple[float, float]:
        if self.inverse_matrix is None:
            raise RuntimeError("Inverse homography matrix not available.")
        pt = np.array([[point_xy[0], point_xy[1], 1.0]], dtype=np.float32).T
        src_pt = self.inverse_matrix @ pt
        src_pt /= src_pt[2]
        return float(src_pt[0]), float(src_pt[1])
