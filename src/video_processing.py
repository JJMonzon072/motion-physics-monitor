"""
Utilidades de entrada/salida de video: lectura, extracción de metadata e iteración de frames.

OpenCV usa el orden de color BGR internamente; los llamadores reciben frames BGR y son
responsables de cualquier conversión de espacio de color necesaria para el rastreo.
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
    """Lee la metadata del video sin decodificar todos los frames."""
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
    Genera pares (índice_frame, frame_bgr) de forma iterativa.

    Parámetros
    ----------
    video_path : ruta al archivo de video.
    skip       : procesa 1 de cada N frames (1 = todos los frames).
    max_frames : límite máximo de frames a procesar para controlar el uso de memoria.
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
    """Guarda un frame BGR anotado en disco como PNG."""
    cv2.imwrite(str(output_path), frame)


def frame_to_rgb(bgr: np.ndarray) -> np.ndarray:
    """Convierte un frame BGR de OpenCV a RGB para mostrarlo en Streamlit."""
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
