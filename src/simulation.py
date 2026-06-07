"""
Generador de datos cinemáticos sintéticos para MRU, MRUV y Caída Libre.

El DataFrame resultante tiene el mismo esquema que la salida del análisis de video,
por lo que puede alimentarse directamente a los módulos de graficación y validación.
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
    Simula Movimiento Rectilíneo Uniforme (MRU): x = x0 + v0·t.

    Parámetros
    ----------
    v0         : velocidad constante [m/s].
    x0         : posición inicial [m].
    total_time : duración de la simulación [s].
    dt         : paso de tiempo [s].
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
    Simula Movimiento Rectilíneo Uniformemente Variado (MRUV):
    x = x0 + v0·t + ½·a·t²,  v = v0 + a·t.

    Parámetros
    ----------
    v0         : velocidad inicial [m/s].
    a0         : aceleración constante [m/s²].
    x0         : posición inicial [m].
    total_time : duración [s].
    dt         : paso de tiempo [s].
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
    Simula Caída Libre: y = y0 + v0·t - ½·g·t²  (Y hacia arriba = positivo).

    La simulación se detiene automáticamente cuando el objeto llega al suelo (y ≤ 0)
    a menos que se especifique total_time.

    Parámetros
    ----------
    y0         : altura inicial [m].
    v0         : velocidad vertical inicial [m/s] (positivo = hacia arriba).
    g          : aceleración gravitacional [m/s²].
    total_time : sobrescribe la parada automática [s].
    dt         : paso de tiempo [s].
    """
    if total_time is None:
        # Discriminante de y0 + v0·t - ½·g·t² = 0
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
    """Construye un DataFrame estandarizado para movimiento horizontal 1-D (MRU/MRUV)."""
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
    Construye un DataFrame estandarizado para movimiento vertical (caída libre).

    Usa y_m para la posición vertical de modo que graficación y clasificación
    detecten correctamente la forma parabólica sobre el eje vertical.
    """
    distance = np.concatenate([[0.0], np.cumsum(np.abs(np.diff(y)))])

    return pd.DataFrame(
        {
            "frame": np.arange(len(t)),
            "time_s": t,
            "x_m": np.zeros_like(t),  # sin desplazamiento horizontal
            "y_m": y,  # posición vertical (altura)
            "position_m": y,  # posición resultante = altura para caída 1-D
            "distance_m": distance,
            "vx_m_s": np.zeros_like(t),
            "vy_m_s": vy,
            "speed_m_s": np.abs(vy),
            "acceleration_m_s2": ay,
            "movement_type": movement_type,
        }
    )
