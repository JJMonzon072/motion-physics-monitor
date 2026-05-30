"""
Object tracking via HSV colour segmentation.

Each frame is converted to HSV, a colour mask is created, morphological
operations clean up noise, and the largest contour's centroid is returned.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

import cv2
import numpy as np

# Pre-defined colour ranges in HSV (H: 0-179, S: 0-255, V: 0-255)
COLOR_PRESETS: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    "Rojo": ((0, 120, 70), (10, 255, 255)),  # uses two ranges due to hue wrap
    "Rojo (alta gama)": ((160, 120, 70), (179, 255, 255)),
    "Azul": ((100, 100, 50), (130, 255, 255)),
    "Verde": ((40, 60, 40), (80, 255, 255)),
    "Amarillo": ((20, 100, 100), (35, 255, 255)),
    "Naranja": ((10, 120, 100), (25, 255, 255)),
}

# Display names shown in the UI dropdown
PRESET_NAMES = ["Rojo", "Azul", "Verde", "Amarillo", "Naranja", "Personalizado"]


@dataclass
class TrackingConfig:
    color_name: str = "Rojo"
    lower_hsv: tuple[int, int, int] = (0, 120, 70)
    upper_hsv: tuple[int, int, int] = (10, 255, 255)
    lower_hsv2: tuple[int, int, int] | None = (160, 120, 70)  # second range for red wrap
    upper_hsv2: tuple[int, int, int] | None = (179, 255, 255)
    min_area: int = 300
    morph_kernel: int = 5


class Detection(NamedTuple):
    x: float
    y: float
    radius: float
    area: float


def get_config_for_color(color_name: str, min_area: int = 300) -> TrackingConfig:
    """Build a TrackingConfig for a named preset colour."""
    if color_name == "Rojo":
        return TrackingConfig(
            color_name="Rojo",
            lower_hsv=(0, 120, 70),
            upper_hsv=(10, 255, 255),
            lower_hsv2=(160, 120, 70),
            upper_hsv2=(179, 255, 255),
            min_area=min_area,
        )
    preset = COLOR_PRESETS.get(color_name)
    if preset is None:
        # Custom or unknown — default to red
        preset = COLOR_PRESETS["Rojo"]
    lower, upper = preset
    return TrackingConfig(
        color_name=color_name,
        lower_hsv=lower,
        upper_hsv=upper,
        lower_hsv2=None,
        upper_hsv2=None,
        min_area=min_area,
    )


def _build_mask(hsv: np.ndarray, cfg: TrackingConfig) -> np.ndarray:
    """Create binary colour mask from HSV frame."""
    lower = np.array(cfg.lower_hsv, dtype=np.uint8)
    upper = np.array(cfg.upper_hsv, dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)

    # Red wraps around H=0/179 — merge second range
    if cfg.lower_hsv2 is not None and cfg.upper_hsv2 is not None:
        lower2 = np.array(cfg.lower_hsv2, dtype=np.uint8)
        upper2 = np.array(cfg.upper_hsv2, dtype=np.uint8)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask, mask2)

    # Morphological cleanup
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (cfg.morph_kernel, cfg.morph_kernel))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    return mask


def detect_object(frame: np.ndarray, cfg: TrackingConfig) -> Detection | None:
    """
    Detect the tracked object in a single BGR frame.

    Returns a Detection named tuple or None if not found.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = _build_mask(hsv, cfg)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Pick largest contour above minimum area threshold
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < cfg.min_area:
        return None

    # Centroid via image moments
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    _, radius = cv2.minEnclosingCircle(largest)

    return Detection(x=cx, y=cy, radius=float(radius), area=float(area))


def annotate_frame(
    frame: np.ndarray,
    detection: Detection | None,
    trajectory: list[tuple[float, float]],
    color: tuple[int, int, int] = (0, 255, 0),
) -> np.ndarray:
    """
    Draw circle, centroid, and trajectory on a copy of the frame.

    Parameters
    ----------
    frame      : BGR source frame.
    detection  : current frame detection (may be None).
    trajectory : list of (x, y) centroids from previous frames.
    color      : BGR draw colour.
    """
    annotated = frame.copy()

    # Draw trajectory as connected dots
    for i in range(1, len(trajectory)):
        pt1 = (int(trajectory[i - 1][0]), int(trajectory[i - 1][1]))
        pt2 = (int(trajectory[i][0]), int(trajectory[i][1]))
        cv2.line(annotated, pt1, pt2, color, 2)

    if detection is not None:
        cx, cy, radius = int(detection.x), int(detection.y), int(detection.radius)
        cv2.circle(annotated, (cx, cy), radius, color, 2)
        cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)  # red centroid dot
        cv2.putText(
            annotated,
            f"({cx}, {cy})",
            (cx + 10, cy - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
        )

    return annotated
