"""
Clasifica el movimiento detectado como MRU, MRUV o Caída Libre.

La clasificación usa regresión por mínimos cuadrados sobre las series de velocidad
y posición para detectar tendencias lineales/cuadráticas, y compara la aceleración
vertical contra g cuando la calibración está disponible.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

GRAVITY = 9.8  # m/s²
FREE_FALL_TOLERANCE = 0.35  # fracción: g experimental debe estar dentro del 35% de 9.8
MRU_ACCEL_THRESHOLD = 0.15  # CV máximo de la velocidad para clasificar como MRU (video real es ruidoso)


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
    """R² de un ajuste lineal por mínimos cuadrados."""
    coeffs = np.polyfit(x, y, 1)
    y_fit = np.polyval(coeffs, x)
    return _r_squared(y, y_fit)


def _quadratic_r2(x: np.ndarray, y: np.ndarray) -> float:
    """R² de un ajuste cuadrático por mínimos cuadrados."""
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
    Clasifica el movimiento a partir de series temporales cinemáticas.

    Parámetros
    ----------
    time         : arreglo de tiempo en segundos.
    position     : posición resultante (escalar) usada para la regresión MRU/MRUV.
    velocity     : serie de rapidez resultante.
    acceleration : serie de aceleración resultante.
    vy           : componente vertical de velocidad (para verificación de caída libre calibrada).
    y_position   : serie de posición vertical (para verificación parabólica sin calibración).
    calibrated   : indica si la posición/aceleración están en unidades SI (metros).
    """
    # Elimina filas NaN antes de la regresión
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

    # --- Verificación de caída libre (calibrada): compara aceleración vertical con g ---
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

    # --- Verificación de caída libre (sin calibrar): ajuste parabólico en posición vertical ---
    if y_position is not None:
        y_mask = ~y_position.isna() & mask
        if int(y_mask.sum()) >= 5:
            y_vals = np.asarray(y_position[y_mask], dtype=float)
            t_y = np.asarray(time[y_mask], dtype=float)
            r2_y_quad = _quadratic_r2(t_y, y_vals)
            r2_y_lin = _linear_r2(t_y, y_vals)
            # Ajuste parabólico claramente mejor que lineal → probablemente caída libre.
            # El umbral 0.02 considera que una parábola puede tener
            # R²_lineal ≈ 0.93 incluso para una curva cuadrática limpia.
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

    # --- MRU / MRUV mediante comparación de R² ---
    r2_pos_linear = _linear_r2(t, pos)
    r2_vel_linear = _linear_r2(t, vel)
    r2_pos_quad = _quadratic_r2(t, pos)

    # Usa el coeficiente de variación de velocidad para distinguir MRU (v constante) de MRUV.
    # acc_std_norm no es confiable: aceleraciones constante-cero (MRU) y constante-nonzero (MRUV)
    # dan std ≈ 0 para datos ideales o simulados.
    vel_mean = abs(float(np.mean(vel)))
    vel_cv = float(np.std(vel)) / (vel_mean + 1e-9)  # CV of speed

    # MRU: velocidad casi constante (CV bajo) Y posición lineal
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

    # MRUV: aceleración constante → velocidad lineal, posición cuadrática
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

    # Sin patrón claro → indeterminado
    return ClassificationResult(
        movement_type="Indeterminado",
        confidence="Baja",
        explanation=(
            "No se identificó un patrón claro de MRU, MRUV o Caída Libre. "
            "El movimiento puede ser complejo, tener mucho ruido, o requerir calibración."
        ),
    )
