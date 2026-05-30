"""
Interactive Plotly charts for kinematic analysis.

All functions return a plotly.graph_objects.Figure so that Streamlit can
render them with st.plotly_chart(fig, use_container_width=True).
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Shared colour palette
COLOR_POS = "#4A90D9"
COLOR_VEL = "#27AE60"
COLOR_ACC = "#E74C3C"
COLOR_TRAJ = "#9B59B6"
FONT_FAMILY = "Inter, Arial, sans-serif"

# Typed as Any so Pyright accepts **_LAYOUT_DEFAULTS in update_layout
_LAYOUT_DEFAULTS: dict[str, Any] = dict(
    font=dict(family=FONT_FAMILY, size=13),
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F8F9FA",
    margin=dict(l=60, r=30, t=60, b=50),
    hovermode="x unified",
)


def _apply_grid(fig: go.Figure) -> go.Figure:
    fig.update_xaxes(showgrid=True, gridcolor="#E0E0E0", zeroline=True, zerolinecolor="#CCCCCC")
    fig.update_yaxes(showgrid=True, gridcolor="#E0E0E0", zeroline=True, zerolinecolor="#CCCCCC")
    return fig


def plot_position(df: pd.DataFrame, unit: str = "m") -> go.Figure:
    """Position vs time chart."""
    pos_col = "position_m" if "position_m" in df.columns else "position_px"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["time_s"],
            y=df[pos_col],
            mode="lines+markers",
            marker=dict(size=4),
            line=dict(color=COLOR_POS, width=2),
            name="Posición",
        )
    )
    fig.update_layout(
        title="Posición vs Tiempo",
        xaxis_title="Tiempo (s)",
        yaxis_title=f"Posición ({unit})",
        **_LAYOUT_DEFAULTS,
    )
    return _apply_grid(fig)


def plot_velocity(df: pd.DataFrame, unit: str = "m/s") -> go.Figure:
    """Speed vs time chart."""
    spd_col = "speed_m_s" if "speed_m_s" in df.columns else "speed_px_s"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["time_s"],
            y=df[spd_col],
            mode="lines+markers",
            marker=dict(size=4),
            line=dict(color=COLOR_VEL, width=2),
            name="Velocidad",
        )
    )
    fig.update_layout(
        title="Velocidad vs Tiempo",
        xaxis_title="Tiempo (s)",
        yaxis_title=f"Velocidad ({unit})",
        **_LAYOUT_DEFAULTS,
    )
    return _apply_grid(fig)


def plot_acceleration(df: pd.DataFrame, unit: str = "m/s²") -> go.Figure:
    """Acceleration vs time chart."""
    acc_col = "acceleration_m_s2" if "acceleration_m_s2" in df.columns else "acceleration_px_s2"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["time_s"],
            y=df[acc_col],
            mode="lines+markers",
            marker=dict(size=4),
            line=dict(color=COLOR_ACC, width=2),
            name="Aceleración",
        )
    )
    fig.update_layout(
        title="Aceleración vs Tiempo",
        xaxis_title="Tiempo (s)",
        yaxis_title=f"Aceleración ({unit})",
        **_LAYOUT_DEFAULTS,
    )
    return _apply_grid(fig)


def plot_trajectory(df: pd.DataFrame, unit: str = "m") -> go.Figure | None:
    """2-D trajectory chart (x vs y). Returns None if data is 1-D only."""
    x_col = "x_m" if "x_m" in df.columns else "x_px"
    y_col = "y_m" if "y_m" in df.columns else "y_px"

    x_series = pd.Series(df[x_col])
    y_series = pd.Series(df[y_col])

    if bool(x_series.isna().all()) or bool(y_series.isna().all()):
        return None

    # Skip if no meaningful 2D spread
    if (x_series.std() or 0.0) < 1e-9 or (y_series.std() or 0.0) < 1e-9:
        return None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            marker=dict(
                size=6,
                color=df["time_s"] if "time_s" in df.columns else None,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="t (s)"),
            ),
            line=dict(color=COLOR_TRAJ, width=1.5),
            name="Trayectoria",
        )
    )
    fig.update_layout(
        title="Trayectoria 2D",
        xaxis_title=f"x ({unit})",
        yaxis_title=f"y ({unit})",
        **_LAYOUT_DEFAULTS,
    )
    return _apply_grid(fig)


def plot_combined_dashboard(df: pd.DataFrame, unit: str = "m") -> go.Figure:
    """Combined 2×2 subplot with position, velocity, acceleration and trajectory."""
    pos_col = "position_m" if "position_m" in df.columns else "position_px"
    spd_col = "speed_m_s" if "speed_m_s" in df.columns else "speed_px_s"
    acc_col = "acceleration_m_s2" if "acceleration_m_s2" in df.columns else "acceleration_px_s2"
    x_col = "x_m" if "x_m" in df.columns else "x_px"
    y_col = "y_m" if "y_m" in df.columns else "y_px"

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "Posición vs Tiempo",
            "Velocidad vs Tiempo",
            "Aceleración vs Tiempo",
            "Trayectoria 2D",
        ],
    )

    t = df["time_s"]
    fig.add_trace(
        go.Scatter(x=t, y=df[pos_col], line=dict(color=COLOR_POS), name="Posición"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=t, y=df[spd_col], line=dict(color=COLOR_VEL), name="Velocidad"),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(x=t, y=df[acc_col], line=dict(color=COLOR_ACC), name="Aceleración"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df[x_col], y=df[y_col], line=dict(color=COLOR_TRAJ), name="Trayectoria"),
        row=2,
        col=2,
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        **_LAYOUT_DEFAULTS,
    )
    return _apply_grid(fig)
