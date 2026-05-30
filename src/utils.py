"""Utility functions: unit conversion, file handling, formatting."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def ensure_output_dir() -> Path:
    """Create data/outputs directory if it doesn't exist and return its path."""
    output_dir = Path("data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def pixels_to_meters(pixels: float, meters_per_pixel: float) -> float:
    """Convert a pixel distance to meters using calibration factor."""
    return pixels * meters_per_pixel


def compute_meters_per_pixel(real_distance_m: float, pixel_distance: float) -> float | None:
    """
    Compute calibration factor from a known real-world reference.
    Returns None if pixel_distance is zero.
    """
    if pixel_distance <= 0:
        return None
    return real_distance_m / pixel_distance


def format_value(value: float, decimals: int = 3, unit: str = "") -> str:
    """Format a numeric value with optional unit string."""
    if unit:
        return f"{value:.{decimals}f} {unit}"
    return f"{value:.{decimals}f}"


def smooth_series(series: pd.Series, window: int = 3) -> pd.Series:
    """Apply centered rolling mean smoothing; fills edges with nearest values."""
    if len(series) < window:
        return series
    # rolling().mean() stubs return DataFrame|Series; re-wrap to guarantee Series
    return pd.Series(
        series.rolling(window=window, center=True, min_periods=1).mean(),
        index=series.index,
        name=series.name,
    )


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide numerator by denominator; return default on zero denominator."""
    if abs(denominator) < 1e-12:
        return default
    return numerator / denominator


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to UTF-8 CSV bytes for Streamlit download."""
    return df.to_csv(index=False).encode("utf-8")


def invert_y_axis(y_values: np.ndarray, frame_height: int) -> np.ndarray:
    """
    Invert Y axis from image convention (origin top-left, Y down) to
    physics convention (origin bottom-left, Y up).
    """
    return frame_height - y_values


def get_temp_video_path(filename: str) -> Path:
    """Return a temp path for storing uploaded videos during processing."""
    temp_dir = Path("data/outputs")
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir / filename
