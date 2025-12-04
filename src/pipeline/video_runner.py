"""
Utility to run the full detection/tracking pipeline over a video and
produce both metrics and 0-99 player ratings.
"""

from pathlib import Path
from typing import Dict, Optional

import cv2

from src.config import PipelineConfig, Paths
from src.pipeline.pipeline import SoccerAnalyticsPipeline, annotate_frame
from src.ratings.rating_engine import rate_players_from_metrics, save_ratings


def _prepare_config(config: Optional[PipelineConfig], model_path: Optional[str], output_dir: Optional[Path]) -> PipelineConfig:
    cfg = config or PipelineConfig()
    if model_path:
        cfg.detection.model_path = model_path
    if output_dir:
        output_dir = Path(output_dir)
        cfg.paths = Paths(output_dir=output_dir, metrics_json=output_dir / "player_metrics.json")
    return cfg


def run_video_analysis(
    video_path: Path,
    config: Optional[PipelineConfig] = None,
    model_path: Optional[str] = None,
    output_dir: Optional[Path] = None,
    save_video_path: Optional[Path] = None,
    display: bool = False,
) -> Dict[str, object]:
    """
    Run detection + tracking on a video, then compute player ratings.

    Returns a dict with paths and rating payload:
    {
        "metrics_path": Path,
        "ratings_path": Path,
        "ratings": Dict,
        "annotated_video_path": Optional[Path],
    }
    """
    cfg = _prepare_config(config, model_path, output_dir)
    pipeline = SoccerAnalyticsPipeline(cfg)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    writer = None
    annotated_video_path = None
    if save_video_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        save_video_path = Path(save_video_path)
        save_video_path.parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(str(save_video_path), fourcc, fps, (width, height))
        annotated_video_path = save_video_path

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        timestamp_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        tracks = pipeline.process_frame(frame, timestamp_s)

        if writer or display:
            annotated = annotate_frame(frame, tracks)
            if writer:
                writer.write(annotated)
            if display:
                cv2.imshow("soccer-analytics", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    metrics_path = pipeline.save_metrics()
    summary_metrics = pipeline.metrics.summarize()
    rating_inputs = pipeline.metrics.to_rating_inputs()
    ratings = rate_players_from_metrics(rating_inputs)
    ratings_path = cfg.paths.output_dir / "player_ratings.json"
    save_ratings(ratings, ratings_path)

    cap.release()
    if writer:
        writer.release()
    if display:
        cv2.destroyAllWindows()

    return {
        "metrics_path": metrics_path,
        "ratings_path": ratings_path,
        "ratings": ratings,
        "metrics_summary": summary_metrics,
        "rating_inputs": rating_inputs,
        "annotated_video_path": annotated_video_path,
    }
