"""
Interactive homography + speed demo.

What it does:
- Load a pitch frame (e.g., first video frame or a still image).
- Manually pick 4 landmarks (corners of the pitch) in clockwise order.
- Compute homography to map image pixels -> metric pitch coords (meters).
- Convert a sequence of player pixel positions to meters and compute speed.

Usage:
    python homography_example.py --image path/to/frame.jpg
Press `q` to quit the image window after selecting points.
"""

import argparse
from typing import List, Tuple

import cv2
import numpy as np


PITCH_WIDTH_M = 68.0   # FIFA standard width
PITCH_HEIGHT_M = 105.0  # FIFA standard height


def collect_points(image) -> List[Tuple[float, float]]:
    """Let user click exactly 4 points in clockwise order starting from top-left."""
    points: List[Tuple[float, float]] = []

    def on_mouse(event, x, y, _flags, _userdata):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(
                image,
                str(len(points)),
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("select 4 corners (clockwise from top-left)", image)

    cv2.imshow("select 4 corners (clockwise from top-left)", image)
    cv2.setMouseCallback("select 4 corners (clockwise from top-left)", on_mouse)

    while len(points) < 4:
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyWindow("select 4 corners (clockwise from top-left)")
    if len(points) != 4:
        raise RuntimeError("Did not receive 4 points. Restart and click 4 pitch corners.")
    return points


def compute_homography(src_pts: List[Tuple[float, float]]) -> np.ndarray:
    """Compute homography from image pixels to metric pitch coords."""
    # Destination: rectangle in meters (origin at top-left corner of pitch)
    dst_pts = np.array(
        [
            [0.0, 0.0],
            [PITCH_WIDTH_M, 0.0],
            [PITCH_WIDTH_M, PITCH_HEIGHT_M],
            [0.0, PITCH_HEIGHT_M],
        ],
        dtype=np.float32,
    )
    src = np.array(src_pts, dtype=np.float32)
    H, _ = cv2.findHomography(src, dst_pts)
    if H is None:
        raise RuntimeError("Homography computation failed.")
    return H


def pixels_to_meters(h_mat: np.ndarray, points_px: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Apply homography to list of pixel points."""
    pts = np.array([[x, y, 1.0] for x, y in points_px], dtype=np.float32).T  # shape (3, N)
    mapped = h_mat @ pts  # shape (3, N)
    mapped /= mapped[2, :]  # normalize
    return [(float(x), float(y)) for x, y in mapped[:2, :].T]


def compute_speeds_mps(positions_m: List[Tuple[float, float]], timestamps_s: List[float]) -> List[float]:
    """Compute per-step speed (m/s) from metric positions and timestamps."""
    speeds: List[float] = []
    for i in range(len(positions_m)):
        if i == 0:
            speeds.append(0.0)
            continue
        dt = max(timestamps_s[i] - timestamps_s[i - 1], 1e-6)
        dist = np.linalg.norm(np.array(positions_m[i]) - np.array(positions_m[i - 1]))
        speeds.append(float(dist / dt))
    return speeds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to a frame showing the full pitch.")
    args = parser.parse_args()

    frame = cv2.imread(args.image)
    if frame is None:
        raise FileNotFoundError(f"Could not read image: {args.image}")

    selection_img = frame.copy()
    src_points = collect_points(selection_img)
    H = compute_homography(src_points)
    print("Homography matrix (pixels -> meters):\n", H)

    # Example: convert some tracked pixel centers to meters and compute speeds.
    example_pixels = [(100, 200), (110, 210), (130, 240), (160, 270)]
    example_timestamps = [0.0, 0.2, 0.4, 0.6]  # seconds
    positions_m = pixels_to_meters(H, example_pixels)
    speeds_mps = compute_speeds_mps(positions_m, example_timestamps)

    print("Pixel positions:", example_pixels)
    print("Metric positions (m):", positions_m)
    print("Speeds (m/s):", speeds_mps)


if __name__ == "__main__":
    main()
