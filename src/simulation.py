"""
Generate synthetic kinematic data for MRU, MRUV, and free fall.

The resulting DataFrame has the same schema as the video-analysis output
so it can be fed directly into plotting and validation modules.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

GRAVITY = 9.8  # m/s²


def simulate_mru(
    v0: float = 2.0,
    x0: float = 0.0,
    total_time: float = 5.0,
    dt: float = 0.05,
) -> pd.DataFrame:
    """
    Simulate Uniform Rectilinear Motion (MRU): x = x0 + v0·t.

    Parameters
    ----------
    v0         : constant velocity [m/s].
    x0         : initial position [m].
    total_time : duration of simulation [s].
    dt         : time step [s].
    """
    t = np.arange(0, total_time + dt, dt)
    x = x0 + v0 * t
    v = np.full_like(t, v0)
    a = np.zeros_like(t)

    return _build_dataframe(t, x, v, a, "MRU")


def simulate_mruv(
    v0: float = 0.0,
    a0: float = 2.0,
    x0: float = 0.0,
    total_time: float = 5.0,
    dt: float = 0.05,
) -> pd.DataFrame:
    """
    Simulate Uniformly Accelerated Rectilinear Motion (MRUV):
    x = x0 + v0·t + ½·a·t²,  v = v0 + a·t.

    Parameters
    ----------
    v0         : initial velocity [m/s].
    a0         : constant acceleration [m/s²].
    x0         : initial position [m].
    total_time : duration [s].
    dt         : time step [s].
    """
    t = np.arange(0, total_time + dt, dt)
    x = x0 + v0 * t + 0.5 * a0 * t**2
    v = v0 + a0 * t
    a = np.full_like(t, a0)

    return _build_dataframe(t, x, v, a, "MRUV")


def simulate_free_fall(
    y0: float = 10.0,
    v0: float = 0.0,
    g: float = GRAVITY,
    total_time: float | None = None,
    dt: float = 0.05,
) -> pd.DataFrame:
    """
    Simulate free fall: y = y0 + v0·t - ½·g·t²  (Y up = positive).

    Simulation stops automatically when the object hits the ground (y ≤ 0)
    unless total_time is specified.

    Parameters
    ----------
    y0         : initial height [m].
    v0         : initial vertical velocity [m/s] (positive = upward).
    g          : gravitational acceleration [m/s²].
    total_time : override automatic stop [s].
    dt         : time step [s].
    """
    if total_time is None:
        # Discriminant of y0 + v0·t - ½·g·t² = 0
        disc = v0**2 + 2.0 * g * y0
        duration: float = 5.0 if disc < 0 else max((v0 + np.sqrt(max(disc, 0.0))) / g, 0.1)
    else:
        duration = total_time

    t = np.arange(0, duration + dt, dt)
    y = y0 + v0 * t - 0.5 * g * t**2

    # Clip at ground level
    ground_idx = np.argmax(y < 0)
    if ground_idx > 0:
        t = t[:ground_idx]
        y = y[:ground_idx]

    v = v0 - g * t
    a = np.full_like(t, -g)

    return _build_dataframe_vertical(t, y, v, a, "Caída Libre")


def _build_dataframe(
    t: np.ndarray,
    position: np.ndarray,
    velocity: np.ndarray,
    acceleration: np.ndarray,
    movement_type: str,
) -> pd.DataFrame:
    """Assemble a standardised DataFrame for horizontal 1-D motion (MRU/MRUV)."""
    distance = np.concatenate([[0.0], np.cumsum(np.abs(np.diff(position)))])

    return pd.DataFrame(
        {
            "frame": np.arange(len(t)),
            "time_s": t,
            "x_m": position,
            "y_m": np.zeros_like(t),
            "position_m": position,
            "distance_m": distance,
            "vx_m_s": velocity,
            "vy_m_s": np.zeros_like(t),
            "speed_m_s": np.abs(velocity),
            "acceleration_m_s2": acceleration,
            "movement_type": movement_type,
        }
    )


def _build_dataframe_vertical(
    t: np.ndarray,
    y: np.ndarray,
    vy: np.ndarray,
    ay: np.ndarray,
    movement_type: str,
) -> pd.DataFrame:
    """
    Assemble a standardised DataFrame for vertical motion (free fall).

    Uses y_m for the vertical position so that plotting and classification
    correctly detect the parabolic shape along the vertical axis.
    """
    distance = np.concatenate([[0.0], np.cumsum(np.abs(np.diff(y)))])

    return pd.DataFrame(
        {
            "frame": np.arange(len(t)),
            "time_s": t,
            "x_m": np.zeros_like(t),  # no horizontal displacement
            "y_m": y,  # vertical position (height)
            "position_m": y,  # resultant position = height for 1-D fall
            "distance_m": distance,
            "vx_m_s": np.zeros_like(t),
            "vy_m_s": vy,
            "speed_m_s": np.abs(vy),
            "acceleration_m_s2": ay,
            "movement_type": movement_type,
        }
    )
