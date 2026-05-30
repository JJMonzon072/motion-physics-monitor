"""
Video I/O helpers: reading, metadata extraction, and frame iteration.

OpenCV uses BGR colour order internally; callers receive BGR frames and are
responsible for any colour-space conversion needed for tracking.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class VideoInfo:
    path: str
    fps: float
    frame_count: int
    width: int
    height: int

    @property
    def duration_s(self) -> float:
        return self.frame_count / self.fps if self.fps > 0 else 0.0

    @property
    def duration_str(self) -> str:
        d = self.duration_s
        return f"{int(d // 60)}:{int(d % 60):02d} min"


def get_video_info(video_path: str | Path) -> VideoInfo:
    """Read video metadata without decoding all frames."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"No se puede abrir el video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    return VideoInfo(
        path=str(video_path),
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
    )


def iter_frames(
    video_path: str | Path,
    skip: int = 1,
    max_frames: int = 2000,
) -> Generator[tuple[int, np.ndarray], None, None]:
    """
    Yield (frame_index, bgr_frame) pairs.

    Parameters
    ----------
    video_path : path to the video file.
    skip       : process every N-th frame (1 = every frame).
    max_frames : hard cap on frames processed to keep memory reasonable.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"No se puede abrir el video: {video_path}")

    idx = 0
    processed = 0

    while processed < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % skip == 0:
            yield idx, frame
            processed += 1
        idx += 1

    cap.release()


def save_annotated_frame(frame: np.ndarray, output_path: str | Path) -> None:
    """Save a single annotated BGR frame to disk (PNG)."""
    cv2.imwrite(str(output_path), frame)


def frame_to_rgb(bgr: np.ndarray) -> np.ndarray:
    """Convert BGR OpenCV frame to RGB for display in Streamlit."""
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
