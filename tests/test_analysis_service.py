import pytest

from pollution_ai.services.analysis_service import AnalysisService


def test_build_spatial_anomaly_result():
    results = [
        {
            "row": 0,
            "col": 0,
            "bbox": [
                17.90,
                59.30,
                18.00,
                59.40,
            ],
            "observed_value": 1900.0,
            "baseline_mean": 1880.0,
            "z_score": 1.2,
        },
        {
            "row": 1,
            "col": 1,
            "bbox": [
                18.00,
                59.40,
                18.10,
                59.50,
            ],
            "observed_value": 1950.0,
            "baseline_mean": 1880.0,
            "z_score": 3.48,
        },
    ]

    result = AnalysisService.build_spatial_anomaly_result(
        results=results,
        pollutant="CH4",
        date="2026-05-09",
        unit="ppb",
    )

    assert result is not None

    assert result.pollutant == "CH4"
    assert result.date == "2026-05-09"
    assert result.latitude == pytest.approx(59.45)
    assert result.longitude == pytest.approx(18.05)

    assert result.observed_value == pytest.approx(1950.0)
    assert result.baseline_mean == pytest.approx(1880.0)
    assert result.z_score == pytest.approx(3.48)

    assert result.unit == "ppb"
    assert result.severity == "high"


def test_build_spatial_anomaly_result_returns_none_without_anomaly():
    results = [
        {
            "row": 0,
            "col": 0,
            "z_score": None,
        }
    ]

    result = AnalysisService.build_spatial_anomaly_result(
        results=results,
        pollutant="CH4",
        date="2026-05-09",
        unit="ppb",
    )

    assert result is None
    
    
def test_build_spatial_anomaly_response_returns_dict():
    results = [
        {
            "row": 0,
            "col": 0,
            "bbox": [
                17.90,
                59.30,
                18.00,
                59.40,
            ],
            "observed_value": 1900.0,
            "baseline_mean": 1880.0,
            "z_score": 1.2,
        },
        {
            "row": 1,
            "col": 1,
            "bbox": [
                18.00,
                59.40,
                18.10,
                59.50,
            ],
            "observed_value": 1950.0,
            "baseline_mean": 1880.0,
            "z_score": 3.48,
        },
    ]

    response = AnalysisService.build_spatial_anomaly_response(
        results=results,
        pollutant="CH4",
        date="2026-05-09",
        unit="ppb",
    )

    assert response == {
    "pollutant": "CH4",
    "date": "2026-05-09",
    "latitude": 59.45,
    "longitude": 18.05,
    "observed_value": 1950.0,
    "baseline_mean": 1880.0,
    "z_score": 3.48,
    "deviation_percent": pytest.approx(
        3.723404255319149
    ),
    "unit": "ppb",
    "severity": "high",
}
    
def test_calculate_coverage():
    results = [
        {
            "observed_value": 1.0,
        },
        {
            "observed_value": None,
        },
        {
            "observed_value": 2.0,
        },
        {
            "observed_value": None,
        },
    ]

    coverage = (
        AnalysisService.calculate_coverage(
            results
        )
    )

    assert coverage == {
        "valid_cells": 2,
        "total_cells": 4,
        "coverage_percent": 50.0,
    }


def test_calculate_coverage_handles_empty_results():
    coverage = (
        AnalysisService.calculate_coverage(
            []
        )
    )

    assert coverage == {
        "valid_cells": 0,
        "total_cells": 0,
        "coverage_percent": 0.0,
    }