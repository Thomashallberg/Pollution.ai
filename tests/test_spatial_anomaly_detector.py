import pytest

from pollution_ai.analysis.spatial_anomaly_detector import (
    build_anomaly_result,
    calculate_spatial_z_score,
    find_strongest_spatial_anomaly,
)


def test_calculate_spatial_z_score():
    z_score = calculate_spatial_z_score(
        observed_value=4.3,
        baseline_mean=1.9,
        baseline_std=0.69,
    )

    assert z_score == pytest.approx(3.48, abs=0.01)


def test_calculate_spatial_z_score_returns_none_without_observation():
    assert (
        calculate_spatial_z_score(
            observed_value=None,
            baseline_mean=1.9,
            baseline_std=0.69,
        )
        is None
    )


def test_calculate_spatial_z_score_returns_none_for_zero_std():
    assert (
        calculate_spatial_z_score(
            observed_value=4.3,
            baseline_mean=1.9,
            baseline_std=0,
        )
        is None
    )


def test_find_strongest_spatial_anomaly():
    results = [
        {
            "row": 0,
            "col": 0,
            "z_score": 1.2,
        },
        {
            "row": 4,
            "col": 3,
            "z_score": 3.48,
        },
        {
            "row": 2,
            "col": 1,
            "z_score": None,
        },
    ]

    strongest = find_strongest_spatial_anomaly(results)

    assert strongest is not None
    assert strongest["row"] == 4
    assert strongest["col"] == 3
    assert strongest["z_score"] == pytest.approx(3.48)


def test_build_anomaly_result():
    strongest = {
        "bbox": [
            17.95,
            59.35,
            18.05,
            59.45,
        ],
        "observed_value": 4.30e-05,
        "baseline_mean": 1.90e-05,
        "z_score": 3.48,
    }

    result = build_anomaly_result(
        strongest=strongest,
        pollutant="NO2",
        date="2026-05-09",
        unit="mol/m²",
    )

    assert result is not None
    assert result.pollutant == "NO2"
    assert result.date == "2026-05-09"

    assert result.latitude == pytest.approx(59.40)
    assert result.longitude == pytest.approx(18.00)

    assert result.observed_value == pytest.approx(4.30e-05)
    assert result.baseline_mean == pytest.approx(1.90e-05)
    assert result.z_score == pytest.approx(3.48)
    assert result.unit == "mol/m²"


def test_build_anomaly_result_returns_none_without_anomaly():
    result = build_anomaly_result(
        strongest=None,
        pollutant="NO2",
        date="2026-05-09",
        unit="mol/m²",
    )

    assert result is None