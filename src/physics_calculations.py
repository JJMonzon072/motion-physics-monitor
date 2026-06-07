"""
Cálculos cinemáticos: posición, velocidad, aceleración, distancia.

Convención de coordenadas
-------------------------
Los frames de video tienen origen en la esquina superior izquierda con Y creciente
hacia abajo. Para el análisis físico, el llamador debe invertir Y antes de pasar los
datos, de modo que Y positivo apunte hacia arriba (convenio físico estándar).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import safe_divide, smooth_series


def build_time_array(n_frames: int, fps: float) -> np.ndarray:
    """Retorna el arreglo de marcas de tiempo [s] para n_frames a los fps indicados."""
    if fps <= 0:
        raise ValueError("Los FPS deben ser positivos.")
    return np.arange(n_frames) / fps


def compute_positions(
    x_pixels: list[float | None],
    y_pixels: list[float | None],
    meters_per_pixel: float | None,
) -> pd.DataFrame:
    """
    Convierte posiciones crudas en píxeles a un DataFrame con conversión a metros opcional.

    Parámetros
    ----------
    x_pixels, y_pixels : listas con None para los frames sin detección.
    meters_per_pixel   : factor de calibración; None conserva las unidades en píxeles.

    Retorna
    -------
    DataFrame con columnas: x_px, y_px, x_m, y_m
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
    Distancia acumulada como longitud de arco a lo largo de la trayectoria.
    Las posiciones NaN aportan 0 distancia (objeto no detectado en ese frame).
    """
    dx = x.diff().fillna(0.0)
    dy = y.diff().fillna(0.0)
    step = np.sqrt(dx**2 + dy**2)
    return step.cumsum()


def compute_velocity(position: pd.Series, time: np.ndarray, smooth_window: int = 3) -> pd.Series:
    """
    Velocidad instantánea mediante diferencias finitas centrales [unidades/s].

    Parámetros
    ----------
    position     : serie 1-D (x, y o resultante) en metros o píxeles.
    time         : arreglo de tiempo correspondiente en segundos.
    smooth_window: ventana de media móvil aplicada a la posición antes de derivar.
    """
    pos_smooth = smooth_series(position, window=smooth_window)
    dt = np.diff(time, prepend=time[0])  # misma longitud que position
    dt[0] = dt[1] if len(dt) > 1 else 1.0  # evita división por cero al inicio

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
    Calcula vx, vy y la rapidez resultante |v| = sqrt(vx² + vy²).

    Retorna
    -------
    vx, vy, speed — todas como pandas Series.
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
    Aceleración instantánea mediante diferencias finitas centrales [unidades/s²].
    La aceleración es inherentemente más ruidosa, por eso se usa una ventana más amplia.
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
    Estadísticas agregadas para mostrar como tarjetas de métricas.

    Retorna dict con claves: avg_velocity, max_velocity, avg_acceleration,
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
    """Construye el DataFrame de exportación con todas las variables cinemáticas."""
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
