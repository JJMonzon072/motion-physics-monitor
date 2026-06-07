"""
Classify detected motion as MRU, MRUV, or free fall.

Classification uses least-squares regression on the velocity and position
series to detect linearity/quadratic trends, and checks the vertical
acceleration against g when calibration is available.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

GRAVITY = 9.8  # m/s²
FREE_FALL_TOLERANCE = 0.35  # fraction: experimental g must be within 35% of 9.8
MRU_ACCEL_THRESHOLD = 0.15  # max CV of speed to call it MRU (real video is noisy)


@dataclass
class ClassificationResult:
    movement_type: str  # "MRU" | "MRUV" | "Caída Libre" | "Indeterminado"
    confidence: str  # "Alta" | "Media" | "Baja"
    explanation: str


def _r_squared(y: np.ndarray, y_fit: np.ndarray) -> float:
    ss_res = np.sum((y - y_fit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot < 1e-12:
        return 1.0
    return float(1.0 - ss_res / ss_tot)


def _linear_r2(x: np.ndarray, y: np.ndarray) -> float:
    """R² of a linear least-squares fit."""
    coeffs = np.polyfit(x, y, 1)
    y_fit = np.polyval(coeffs, x)
    return _r_squared(y, y_fit)


def _quadratic_r2(x: np.ndarray, y: np.ndarray) -> float:
    """R² of a quadratic least-squares fit."""
    coeffs = np.polyfit(x, y, 2)
    y_fit = np.polyval(coeffs, x)
    return _r_squared(y, y_fit)


def classify_motion(
    time: np.ndarray,
    position: pd.Series,
    velocity: pd.Series,
    acceleration: pd.Series,
    vy: pd.Series | None = None,
    y_position: pd.Series | None = None,
    calibrated: bool = False,
) -> ClassificationResult:
    """
    Classify movement from kinematic time series.

    Parameters
    ----------
    time       : time array in seconds.
    position   : resultant (scalar) position used for MRU/MRUV regression.
    velocity   : resultant speed series.
    acceleration : resultant acceleration series.
    vy         : vertical velocity component (used for calibrated free-fall check).
    y_position : vertical position series (used for parabolic free-fall check
                 even without calibration).
    calibrated : whether position/acceleration are in SI units (metres).
    """
    # Drop NaN rows for regression
    mask = ~(position.isna() | velocity.isna() | acceleration.isna())
    t = np.asarray(time[mask], dtype=float)
    pos = np.asarray(position[mask], dtype=float)
    vel = np.asarray(velocity[mask], dtype=float)

    if len(t) < 5:
        return ClassificationResult(
            movement_type="Indeterminado",
            confidence="Baja",
            explanation="Datos insuficientes para clasificar el movimiento (menos de 5 puntos detectados).",
        )

    # --- Free-fall check (calibrated): compare vertical accel against g ---
    if calibrated and vy is not None:
        vy_clean = np.asarray(vy[mask], dtype=float)
        ay_coeffs = np.polyfit(t, vy_clean, 1)
        ay_exp = abs(ay_coeffs[0])  # slope of vy vs t = vertical acceleration
        if abs(ay_exp - GRAVITY) / GRAVITY < FREE_FALL_TOLERANCE:
            r2_quad = _quadratic_r2(t, pos)
            conf = "Alta" if r2_quad > 0.90 else "Media"
            return ClassificationResult(
                movement_type="Caída Libre",
                confidence=conf,
                explanation=(
                    f"Aceleración vertical experimental: {ay_exp:.2f} m/s² "
                    f"(~{(ay_exp / GRAVITY) * 100:.0f}% de g = 9.8 m/s²). "
                    "La posición sigue una curva parabólica característica de la caída libre."
                ),
            )

    # --- Free-fall check (uncalibrated): parabolic fit on vertical position ---
    if y_position is not None:
        y_mask = ~y_position.isna() & mask
        if int(y_mask.sum()) >= 5:
            y_vals = np.asarray(y_position[y_mask], dtype=float)
            t_y = np.asarray(time[y_mask], dtype=float)
            r2_y_quad = _quadratic_r2(t_y, y_vals)
            r2_y_lin = _linear_r2(t_y, y_vals)
            # Parabolic fit clearly better than linear → likely free fall.
            # Threshold 0.05 accounts for the fact that a parabola can have
            # R²_linear ≈ 0.93 even for a clean quadratic curve.
            if r2_y_quad > 0.75 and (r2_y_quad - r2_y_lin) > 0.02:
                conf = "Alta" if r2_y_quad > 0.92 else "Media"
                return ClassificationResult(
                    movement_type="Caída Libre",
                    confidence=conf,
                    explanation=(
                        f"La posición vertical sigue una tendencia parabólica "
                        f"(R²={r2_y_quad:.2f}), característica de la caída libre. "
                        "Sin calibración no se puede comparar con g = 9.8 m/s², "
                        "pero el comportamiento cinemático es consistente con caída libre."
                    ),
                )

    # --- MRU / MRUV via R² comparison ---
    r2_pos_linear = _linear_r2(t, pos)
    r2_vel_linear = _linear_r2(t, vel)
    r2_pos_quad = _quadratic_r2(t, pos)

    # Use velocity coefficient of variation to distinguish MRU (constant v) from MRUV.
    # acc_std_norm is unreliable: both constant-zero (MRU) and constant-nonzero (MRUV)
    # accelerations give std ≈ 0 for ideal/simulated data.
    vel_mean = abs(float(np.mean(vel)))
    vel_cv = float(np.std(vel)) / (vel_mean + 1e-9)  # CV of speed

    # MRU: velocity nearly constant (low CV) AND position linear
    if vel_cv < MRU_ACCEL_THRESHOLD and r2_pos_linear > 0.90:
        conf = "Alta" if r2_pos_linear > 0.95 else "Media"
        return ClassificationResult(
            movement_type="MRU",
            confidence=conf,
            explanation=(
                f"Velocidad aproximadamente constante (coeficiente de variación: "
                f"{vel_cv:.3f}). "
                f"La posición muestra tendencia lineal (R²={r2_pos_linear:.2f}), "
                "característica del Movimiento Rectilíneo Uniforme."
            ),
        )

    # MRUV: constant acceleration → velocity is linear, position is quadratic
    if r2_vel_linear > 0.75 and r2_pos_quad > 0.75:
        conf = "Alta" if (r2_vel_linear > 0.90 and r2_pos_quad > 0.90) else "Media"
        return ClassificationResult(
            movement_type="MRUV",
            confidence=conf,
            explanation=(
                f"La velocidad muestra tendencia lineal (R²={r2_vel_linear:.2f}) y "
                f"la posición comportamiento cuadrático (R²={r2_pos_quad:.2f}), "
                "indicando aceleración aproximadamente constante: Movimiento Rectilíneo Uniformemente Variado."
            ),
        )

    # Undetermined if no pattern is clear
    return ClassificationResult(
        movement_type="Indeterminado",
        confidence="Baja",
        explanation=(
            "No se identificó un patrón claro de MRU, MRUV o Caída Libre. "
            "El movimiento puede ser complejo, tener mucho ruido, o requerir calibración."
        ),
    )
