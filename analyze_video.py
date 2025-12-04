"""
CLI entrypoint to let a user supply a soccer match video, run the vision
pipeline, and output per-player 0-99 ratings.
"""

import argparse
import json
from pathlib import Path

from src.pipeline.video_runner import run_video_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a match video and compute player ratings.")
    parser.add_argument("--video", required=True, help="Path to the input match video.")
    parser.add_argument("--model", default="yolov8n.pt", help="Path to a YOLOv8 weights file.")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Where to store metrics/ratings. Defaults to outputs/<video-stem>/",
    )
    parser.add_argument(
        "--save-video",
        default=None,
        help="Optional path to save an annotated video (e.g. outputs/annotated.mp4).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display a live preview with bounding boxes while processing.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    video_path = Path(args.video)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    default_output = Path("outputs") / video_path.stem
    output_dir = Path(args.output_dir) if args.output_dir else default_output
    save_video_path = Path(args.save_video) if args.save_video else None

    result = run_video_analysis(
        video_path=video_path,
        model_path=args.model,
        output_dir=output_dir,
        save_video_path=save_video_path,
        display=args.show,
    )

    print(f"Metrics saved to: {result['metrics_path']}")
    print(f"Ratings saved to: {result['ratings_path']}")
    if result["annotated_video_path"]:
        print(f"Annotated video saved to: {result['annotated_video_path']}")
    print("Ratings payload:")
    print(json.dumps(result["ratings"], indent=2))
    if result.get("metrics_summary"):
        print("Metrics summary (per track id):")
        print(json.dumps(result["metrics_summary"], indent=2))


if __name__ == "__main__":
    main()
