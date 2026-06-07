"""
Validación: compara resultados experimentales contra valores teóricos.

Calcula el error absoluto, el error porcentual y retorna un reporte estructurado.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

GRAVITY = 9.8  # m/s²


@dataclass
class ValidationResult:
    variable: str
    theoretical: float
    experimental: float
    absolute_error: float
    percent_error: float
    unit: str
    interpretation: str


def _interpret_error(percent_error: float) -> str:
    if percent_error < 5.0:
        return "Excelente precisión: el error es menor al 5%."
    elif percent_error < 15.0:
        return "Buena precisión: el error está entre 5% y 15%, aceptable para video."
    elif percent_error < 30.0:
        return "Precisión moderada: el error está entre 15% y 30%. Puede mejorar con mejor calibración o iluminación."
    else:
        return (
            "Error alto (>30%). Revisar calibración, calidad del video o condiciones de grabación."
        )


def validate_single(
    variable: str,
    theoretical: float,
    experimental: float,
    unit: str = "",
) -> ValidationResult:
    """Compara una medición experimental contra su valor teórico."""
    if abs(theoretical) < 1e-12:
        abs_err = abs(experimental - theoretical)
        pct_err = 0.0 if abs_err < 1e-12 else float("inf")
    else:
        abs_err = abs(experimental - theoretical)
        pct_err = abs_err / abs(theoretical) * 100.0

    return ValidationResult(
        variable=variable,
        theoretical=theoretical,
        experimental=experimental,
        absolute_error=abs_err,
        percent_error=pct_err,
        unit=unit,
        interpretation=_interpret_error(pct_err),
    )


def validate_mru(theoretical_velocity: float, experimental_velocity: float) -> ValidationResult:
    """Valida MRU: compara las velocidades promedio."""
    return validate_single(
        variable="Velocidad promedio (MRU)",
        theoretical=theoretical_velocity,
        experimental=experimental_velocity,
        unit="m/s",
    )


def validate_mruv(
    theoretical_acceleration: float, experimental_acceleration: float
) -> ValidationResult:
    """Valida MRUV: compara las aceleraciones promedio."""
    return validate_single(
        variable="Aceleración promedio (MRUV)",
        theoretical=theoretical_acceleration,
        experimental=experimental_acceleration,
        unit="m/s²",
    )


def validate_free_fall(experimental_acceleration: float) -> ValidationResult:
    """Valida caída libre: compara la aceleración vertical experimental contra g."""
    return validate_single(
        variable="Aceleración gravitacional (Caída Libre)",
        theoretical=GRAVITY,
        experimental=experimental_acceleration,
        unit="m/s²",
    )


def results_to_dataframe(results: list[ValidationResult]) -> pd.DataFrame:
    """Convierte una lista de ValidationResult en un DataFrame listo para mostrar."""
    rows = [
        {
            "Variable": r.variable,
            f"Teórico ({r.unit})": f"{r.theoretical:.4f}",
            f"Experimental ({r.unit})": f"{r.experimental:.4f}",
            "Error Absoluto": f"{r.absolute_error:.4f} {r.unit}",
            "Error %": f"{r.percent_error:.2f}%",
            "Interpretación": r.interpretation,
        }
        for r in results
    ]
    return pd.DataFrame(rows)
