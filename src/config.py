from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class DetectionConfig:
    """Configuration for YOLOv8 detection."""

    model_path: str = "yolov8n.pt"
    device: str = "cpu"
    class_map: Dict[str, int] = field(
        default_factory=lambda: {"player": 0, "ball": 32, "referee": 0}
    )
    conf_threshold: float = 0.3
    iou_threshold: float = 0.45


@dataclass
class TrackingConfig:
    """Configuration for ByteTrack tracker."""

    track_thresh: float = 0.4
    match_thresh: float = 0.9
    track_buffer: int = 30
    mot20: bool = False


@dataclass
class HomographyConfig:
    """Configuration for homography mapping."""

    pitch_width_m: float = 68.0
    pitch_height_m: float = 105.0
    reference_points_src: Optional[list] = None
    reference_points_dst: Optional[list] = None


@dataclass
class Paths:
    """Filesystem paths used by the pipeline."""

    output_dir: Path = Path("outputs")
    metrics_json: Path = output_dir / "player_metrics.json"


@dataclass
class PipelineConfig:
    detection: DetectionConfig = DetectionConfig()
    tracking: TrackingConfig = TrackingConfig()
    homography: HomographyConfig = HomographyConfig()
    paths: Paths = Paths()
