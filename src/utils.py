"""Funciones auxiliares: conversión de unidades, manejo de archivos y formato."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def ensure_output_dir() -> Path:
    """Crea el directorio data/outputs si no existe y retorna su ruta."""
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def pixels_to_meters(pixels: float, meters_per_pixel: float) -> float:
    """Convierte una distancia en píxeles a metros usando el factor de calibración."""
    return pixels * meters_per_pixel


def compute_meters_per_pixel(real_distance_m: float, pixel_distance: float) -> float | None:
    """
    Calcula el factor de calibración a partir de una referencia real conocida.
    Retorna None si pixel_distance es cero.
    """
    if pixel_distance <= 0:
        return None
    return real_distance_m / pixel_distance


def format_value(value: float, decimals: int = 3, unit: str = "") -> str:
    """Formatea un valor numérico con decimales y unidad opcional."""
    if unit:
        return f"{value:.{decimals}f} {unit}"
    return f"{value:.{decimals}f}"


def smooth_series(series: pd.Series, window: int = 3) -> pd.Series:
    """Aplica suavizado por media móvil centrada; los bordes se rellenan con vecinos."""
    if len(series) < window:
        return series
    # rolling().mean() puede retornar DataFrame|Series; re-envolver garantiza Series
    return pd.Series(
        series.rolling(window=window, center=True, min_periods=1).mean(),
        index=series.index,
        name=series.name,
    )


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide numerador entre denominador; retorna default si el denominador es cero."""
    if abs(denominator) < 1e-12:
        return default
    return numerator / denominator


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes UTF-8 en formato CSV para descarga en Streamlit."""
    return df.to_csv(index=False).encode("utf-8")


def invert_y_axis(y_values: np.ndarray, frame_height: int) -> np.ndarray:
    """
    Invierte el eje Y del convenio de imagen (origen arriba-izquierda, Y↓) al
    convenio físico (origen abajo-izquierda, Y↑).
    """
    return frame_height - y_values


def get_temp_video_path(filename: str) -> Path:
    """Retorna la ruta temporal para almacenar videos subidos durante el procesamiento."""
    temp_dir = Path("data/outputs")
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir / filename
