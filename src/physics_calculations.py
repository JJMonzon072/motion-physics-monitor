"""
Kinematics calculations: position, velocity, acceleration, distance.

Coordinate convention
---------------------
Video frames have origin at top-left with Y increasing downward.
For physics analysis the caller should invert Y before passing data so that
positive Y means upward (standard physics convention).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import safe_divide, smooth_series


def build_time_array(n_frames: int, fps: float) -> np.ndarray:
    """Return array of time stamps [s] for n_frames at given fps."""
    if fps <= 0:
        raise ValueError("FPS must be positive.")
    return np.arange(n_frames) / fps


def compute_positions(
    x_pixels: list[float | None],
    y_pixels: list[float | None],
    meters_per_pixel: float | None,
) -> pd.DataFrame:
    """
    Convert raw pixel positions to a DataFrame with optional meter conversion.

    Parameters
    ----------
    x_pixels, y_pixels : lists with None for undetected frames.
    meters_per_pixel   : calibration factor; None means keep pixel units.

    Returns
    -------
    DataFrame with columns: x_px, y_px, x_m, y_m
    """
    x_arr = np.array([v if v is not None else np.nan for v in x_pixels], dtype=float)
    y_arr = np.array([v if v is not None else np.nan for v in y_pixels], dtype=float)

    df = pd.DataFrame({"x_px": x_arr, "y_px": y_arr})

    if meters_per_pixel is not None:
        df["x_m"] = df["x_px"] * meters_per_pixel
        df["y_m"] = df["y_px"] * meters_per_pixel
    else:
        df["x_m"] = np.nan
        df["y_m"] = np.nan

    return df


def compute_distance(x: pd.Series, y: pd.Series) -> pd.Series:
    """
    Cumulative arc-length distance along the trajectory.
    NaN positions contribute 0 distance (object not detected).
    """
    dx = x.diff().fillna(0.0)
    dy = y.diff().fillna(0.0)
    step = np.sqrt(dx**2 + dy**2)
    return step.cumsum()


def compute_velocity(position: pd.Series, time: np.ndarray, smooth_window: int = 3) -> pd.Series:
    """
    Instantaneous velocity via central finite differences [units/s].

    Parameters
    ----------
    position     : 1-D series (x, y, or resultant) in meters or pixels.
    time         : matching time array in seconds.
    smooth_window: rolling-mean window applied to position before differentiation.
    """
    pos_smooth = smooth_series(position, window=smooth_window)
    dt = np.diff(time, prepend=time[0])  # same length as position
    dt[0] = dt[1] if len(dt) > 1 else 1.0  # avoid zero at start

    dp = pos_smooth.diff().fillna(0.0).values
    vel = np.array([safe_divide(dp[i], dt[i]) for i in range(len(dp))])
    return pd.Series(vel, index=position.index, name=position.name)


def compute_velocity_2d(
    x: pd.Series,
    y: pd.Series,
    time: np.ndarray,
    smooth_window: int = 3,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Compute vx, vy and resultant speed |v| = sqrt(vx² + vy²).

    Returns
    -------
    vx, vy, speed  — all as pandas Series.
    """
    vx = compute_velocity(x, time, smooth_window)
    vy = compute_velocity(y, time, smooth_window)
    speed = np.sqrt(vx**2 + vy**2)
    speed.name = "speed"
    return vx, vy, speed


def compute_acceleration(
    velocity: pd.Series, time: np.ndarray, smooth_window: int = 5
) -> pd.Series:
    """
    Instantaneous acceleration via central finite differences [units/s²].
    Acceleration is inherently noisier, so a wider default smooth_window is used.
    """
    vel_smooth = smooth_series(velocity, window=smooth_window)
    dt = np.diff(time, prepend=time[0])
    dt[0] = dt[1] if len(dt) > 1 else 1.0

    dv = vel_smooth.diff().fillna(0.0).values
    acc = np.array([safe_divide(dv[i], dt[i]) for i in range(len(dv))])
    return pd.Series(acc, index=velocity.index, name=velocity.name)


def compute_summary_stats(
    velocity: pd.Series, acceleration: pd.Series, distance: pd.Series
) -> dict[str, float]:
    """
    Aggregate statistics for display as metric cards.

    Returns dict with keys: avg_velocity, max_velocity, avg_acceleration,
    max_acceleration, total_distance.
    """
    valid_v = velocity.dropna()
    valid_a = acceleration.dropna()

    return {
        "avg_velocity": float(valid_v.mean()) if len(valid_v) > 0 else 0.0,
        "max_velocity": float(valid_v.abs().max()) if len(valid_v) > 0 else 0.0,
        "avg_acceleration": float(valid_a.mean()) if len(valid_a) > 0 else 0.0,
        "max_acceleration": float(valid_a.abs().max()) if len(valid_a) > 0 else 0.0,
        "total_distance": float(distance.iloc[-1]) if len(distance) > 0 else 0.0,
    }


def build_results_dataframe(
    frames: list[int],
    time: np.ndarray,
    x_px: pd.Series,
    y_px: pd.Series,
    x_m: pd.Series,
    y_m: pd.Series,
    distance: pd.Series,
    vx: pd.Series,
    vy: pd.Series,
    speed: pd.Series,
    acceleration: pd.Series,
    movement_type: str,
    calibrated: bool,
) -> pd.DataFrame:
    """Assemble a tidy export DataFrame."""
    pos_col = "position_m" if calibrated else "position_px"
    pos_vals = np.sqrt(x_m**2 + y_m**2) if calibrated else np.sqrt(x_px**2 + y_px**2)

    df = pd.DataFrame(
        {
            "frame": frames,
            "time_s": time,
            "x_px": x_px.values,
            "y_px": y_px.values,
            "x_m": x_m.values,
            "y_m": y_m.values,
            pos_col: pos_vals.values,
            "distance_m" if calibrated else "distance_px": distance.values,
            "vx_m_s" if calibrated else "vx_px_s": vx.values,
            "vy_m_s" if calibrated else "vy_px_s": vy.values,
            "speed_m_s" if calibrated else "speed_px_s": speed.values,
            "acceleration_m_s2" if calibrated else "acceleration_px_s2": acceleration.values,
            "movement_type": movement_type,
        }
    )
    return df
