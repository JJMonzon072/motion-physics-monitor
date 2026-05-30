"""
Unit tests for physics_calculations module.

Verifies correctness of time arrays, velocity, acceleration,
distance, and summary statistics using known kinematic scenarios.
"""

import numpy as np
import pandas as pd
import pytest

from src.motion_classification import classify_motion
from src.physics_calculations import (
    build_time_array,
    compute_acceleration,
    compute_distance,
    compute_positions,
    compute_summary_stats,
    compute_velocity,
    compute_velocity_2d,
)
from src.simulation import simulate_free_fall, simulate_mru, simulate_mruv
from src.utils import compute_meters_per_pixel, safe_divide, smooth_series
from src.validation import validate_free_fall, validate_mru, validate_mruv

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mru_data():
    """Uniform motion: x = 2t, v = 2 m/s, a = 0."""
    fps = 30.0
    t = np.arange(0, 3.0, 1 / fps)
    x = 2.0 * t  # v = 2 m/s
    return t, x


@pytest.fixture
def mruv_data():
    """Uniformly accelerated: x = 0.5*a*t^2, v = a*t, a = 4 m/s²."""
    fps = 30.0
    t = np.arange(0, 3.0, 1 / fps)
    a = 4.0
    x = 0.5 * a * t**2
    return t, x, a


# ── Time array ────────────────────────────────────────────────────────────────


def test_build_time_array_length():
    t = build_time_array(90, 30.0)
    assert len(t) == 90


def test_build_time_array_values():
    t = build_time_array(4, 2.0)
    expected = np.array([0.0, 0.5, 1.0, 1.5])
    np.testing.assert_allclose(t, expected)


def test_build_time_array_invalid_fps():
    with pytest.raises(ValueError):
        build_time_array(10, 0.0)


# ── Positions ─────────────────────────────────────────────────────────────────


def test_compute_positions_calibrated():
    df = compute_positions([100.0, 200.0, 300.0], [0.0, 0.0, 0.0], meters_per_pixel=0.01)
    assert "x_m" in df.columns
    np.testing.assert_allclose(_col(df, "x_m").to_numpy(), [1.0, 2.0, 3.0])


def test_compute_positions_no_calibration():
    df = compute_positions([100.0, 200.0], [50.0, 60.0], meters_per_pixel=None)
    assert bool(_col(df, "x_m").isna().all())
    assert bool(_col(df, "y_m").isna().all())


def test_compute_positions_with_none():
    df = compute_positions([100.0, None, 300.0], [0.0, None, 0.0], meters_per_pixel=0.01)
    assert np.isnan(df["x_m"].iloc[1])


# ── Velocity ──────────────────────────────────────────────────────────────────


def test_velocity_mru(mru_data):
    """MRU: velocity should be approximately constant at 2 m/s."""
    t, x = mru_data
    x_series = pd.Series(x)
    vel = compute_velocity(x_series, t, smooth_window=1)
    # Ignore first point (boundary effect); check bulk
    np.testing.assert_allclose(vel.iloc[5:-5].mean(), 2.0, rtol=0.05)


def test_velocity_2d_resultant():
    """Resultant speed equals scalar velocity for 1-D motion."""
    fps = 10.0
    t = np.arange(0, 2.0, 1 / fps)
    x = pd.Series(3.0 * t)
    y = pd.Series(np.zeros(len(t)))
    _vx, _vy, speed = compute_velocity_2d(x, y, t, smooth_window=1)
    np.testing.assert_allclose(speed.iloc[5:-5].mean(), 3.0, rtol=0.05)


# ── Acceleration ──────────────────────────────────────────────────────────────


def test_acceleration_mruv(mruv_data):
    """MRUV: average acceleration should be close to 4 m/s²."""
    t, x, expected_a = mruv_data
    x_series = pd.Series(x)
    vel = compute_velocity(x_series, t, smooth_window=3)
    acc = compute_acceleration(vel, t, smooth_window=5)
    # Check bulk (skip transients at edges)
    mean_acc = acc.iloc[10:-10].mean()
    assert (
        abs(mean_acc - expected_a) / expected_a < 0.10
    ), f"Expected ~{expected_a} m/s², got {mean_acc:.3f}"


def test_acceleration_mru_near_zero(mru_data):
    """MRU: acceleration should be close to zero."""
    t, x = mru_data
    x_series = pd.Series(x)
    vel = compute_velocity(x_series, t, smooth_window=3)
    acc = compute_acceleration(vel, t, smooth_window=5)
    assert abs(acc.iloc[10:-10].mean()) < 0.5


# ── Distance ──────────────────────────────────────────────────────────────────


def test_distance_linear():
    """Straight-line motion: distance = final_pos - initial_pos."""
    x = pd.Series([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    y = pd.Series([0.0] * 6)
    d = compute_distance(x, y)
    assert abs(d.iloc[-1] - 5.0) < 1e-9


def test_distance_always_non_decreasing():
    """Distance should never decrease."""
    x = pd.Series([0.0, 1.0, 0.5, 1.5, 1.0, 2.0])
    y = pd.Series([0.0] * 6)
    d = compute_distance(x, y)
    diffs = d.diff().fillna(0.0)
    assert (diffs >= -1e-9).all()


# ── Summary stats ─────────────────────────────────────────────────────────────


def test_summary_stats_keys():
    vel = pd.Series([1.0, 2.0, 3.0])
    acc = pd.Series([0.5, 0.5, 0.5])
    dist = pd.Series([0.0, 1.0, 2.0])
    stats = compute_summary_stats(vel, acc, dist)
    assert "avg_velocity" in stats
    assert "max_velocity" in stats
    assert "total_distance" in stats


def test_summary_stats_values():
    vel = pd.Series([2.0, 4.0, 6.0])
    acc = pd.Series([1.0, 1.0, 1.0])
    dist = pd.Series([0.0, 2.0, 5.0])
    stats = compute_summary_stats(vel, acc, dist)
    assert abs(stats["avg_velocity"] - 4.0) < 1e-9
    assert abs(stats["max_velocity"] - 6.0) < 1e-9
    assert abs(stats["total_distance"] - 5.0) < 1e-9


# ── Utils ─────────────────────────────────────────────────────────────────────


def test_safe_divide_normal():
    assert abs(safe_divide(10.0, 4.0) - 2.5) < 1e-9


def test_safe_divide_zero():
    assert safe_divide(5.0, 0.0, default=-1.0) == -1.0


def test_meters_per_pixel():
    mpp = compute_meters_per_pixel(1.0, 200.0)
    assert mpp is not None
    assert abs(mpp - 0.005) < 1e-9


def test_meters_per_pixel_zero():
    assert compute_meters_per_pixel(1.0, 0.0) is None


def test_smooth_series():
    s = pd.Series([1.0, 3.0, 5.0, 7.0, 9.0])
    smooth = smooth_series(s, window=3)
    assert len(smooth) == len(s)
    # Middle value should be average of neighbours
    assert abs(smooth.iloc[2] - 5.0) < 0.1


# ── Validation ────────────────────────────────────────────────────────────────


def test_validate_mru_low_error():
    r = validate_mru(2.0, 2.05)
    assert r.percent_error < 5.0


def test_validate_mruv_high_error():
    r = validate_mruv(4.0, 6.0)
    assert r.percent_error > 30.0


def test_validate_free_fall_exact():
    r = validate_free_fall(9.8)
    assert r.percent_error < 1e-6


def test_validate_interpretation_excellent():
    r = validate_mru(5.0, 5.1)
    assert "Excelente" in r.interpretation


def test_validate_interpretation_high_error():
    r = validate_mru(1.0, 2.0)
    assert (
        "alto" in r.interpretation.lower()
        or "mayor" in r.interpretation.lower()
        or "30" in r.interpretation
    )


# ── Classification ────────────────────────────────────────────────────────────


def _col(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.Series(df[col])


def test_classify_mru_from_simulation():
    """Simulated MRU data should classify as MRU."""
    df = simulate_mru(v0=2.0, total_time=3.0)
    result = classify_motion(
        _col(df, "time_s").to_numpy(),
        _col(df, "position_m"),
        _col(df, "speed_m_s"),
        _col(df, "acceleration_m_s2"),
    )
    assert result.movement_type == "MRU"


def test_classify_mruv_from_simulation():
    """Simulated MRUV data should classify as MRUV."""
    df = simulate_mruv(v0=0.0, a0=3.0, total_time=3.0)
    result = classify_motion(
        _col(df, "time_s").to_numpy(),
        _col(df, "position_m"),
        _col(df, "speed_m_s"),
        _col(df, "acceleration_m_s2"),
    )
    assert result.movement_type == "MRUV"


def test_classify_free_fall_uncalibrated_via_y_position():
    """Free fall should be detected via parabolic y_position even without calibration."""
    df = simulate_free_fall(y0=10.0, v0=0.0, g=9.8)
    result = classify_motion(
        _col(df, "time_s").to_numpy(),
        _col(df, "position_m"),
        _col(df, "speed_m_s"),
        _col(df, "acceleration_m_s2"),
        y_position=_col(df, "y_m"),
        calibrated=False,
    )
    assert result.movement_type == "Caída Libre"


def test_classify_free_fall_calibrated():
    """Free fall with calibration should be detected via vertical acceleration."""
    df = simulate_free_fall(y0=10.0, v0=0.0, g=9.8)
    result = classify_motion(
        _col(df, "time_s").to_numpy(),
        _col(df, "position_m"),
        _col(df, "speed_m_s"),
        _col(df, "acceleration_m_s2"),
        vy=_col(df, "vy_m_s"),
        calibrated=True,
    )
    assert result.movement_type == "Caída Libre"


def test_free_fall_simulation_uses_y_m():
    """Free fall simulation must store height in y_m, not x_m."""
    df = simulate_free_fall(y0=5.0)
    assert _col(df, "y_m").iloc[0] == pytest.approx(5.0, abs=0.1)
    assert (_col(df, "x_m") == 0.0).all()
