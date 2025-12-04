"""
Example usage of the modular soccer analytics pipeline.

This script reads a video, performs detection + tracking, clusters teams,
maps to pitch coordinates, and accumulates speed/distance metrics.
"""

import argparse

import cv2

from src.config import PipelineConfig
from src.pipeline.pipeline import SoccerAnalyticsPipeline, annotate_frame


def parse_args():
    parser = argparse.ArgumentParser(description="Soccer analytics starter pipeline")
    parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLOv8 model path")
    parser.add_argument("--save-video", type=str, default=None, help="Optional path to save annotated video")
    return parser.parse_args()


def main():
    args = parse_args()
    config = PipelineConfig()
    config.detection.model_path = args.model

    pipeline = SoccerAnalyticsPipeline(config)

    cap = cv2.VideoCapture(args.video)
    writer = None
    if args.save_video:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(args.save_video, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        timestamp_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        tracks = pipeline.process_frame(frame, timestamp_s)
        annotated = annotate_frame(frame, tracks)
        if writer:
            writer.write(annotated)
        cv2.imshow("soccer-analytics", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    metrics_path = pipeline.save_metrics()
    print(f"Saved metrics to {metrics_path}")
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
