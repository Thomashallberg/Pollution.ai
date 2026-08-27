import pytest
from fastapi.testclient import TestClient

from pollution_ai.api.app import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "pollution-ai",
    }


def test_get_spatial_ch4_anomaly():
    response = client.get(
        "/api/anomalies/spatial"
        "?pollutant=CH4"
        "&date=2026-05-09"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pollutant"] == "CH4"
    assert data["date"] == "2026-05-09"
    assert data["unit"] == "ppb"

    assert data["latitude"] == pytest.approx(
        59.44375
    )

    assert data["longitude"] == pytest.approx(
        18.10625
    )

    assert data["observed_value"] == pytest.approx(
        1910.0,
        rel=0.01,
    )

    assert data["baseline_mean"] == pytest.approx(
        1878.0,
        rel=0.01,
    )

    assert data["z_score"] == pytest.approx(
        1.60,
        abs=0.01,
    )

    assert data["severity"] == "low"


def test_get_spatial_no2_anomaly():
    response = client.get(
        "/api/anomalies/spatial"
        "?pollutant=NO2"
        "&date=2026-05-09"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pollutant"] == "NO2"
    assert data["date"] == "2026-05-09"
    assert data["unit"] == "mol/m²"

    assert data["z_score"] == pytest.approx(
        3.48,
        abs=0.01,
    )

    assert data["severity"] == "high"


def test_get_spatial_anomaly_rejects_unknown_pollutant():
    response = client.get(
        "/api/anomalies/spatial"
        "?pollutant=banana"
        "&date=2026-05-09"
    )

    assert response.status_code == 422


def test_get_spatial_ch4_cells():
    response = client.get(
        "/api/spatial/cells"
        "?pollutant=CH4"
        "&date=2026-05-09"
    )

    assert response.status_code == 200

    cells = response.json()

    assert len(cells) > 0

    first_cell = cells[0]

    assert first_cell["row"] == 0
    assert first_cell["col"] == 0
    assert first_cell["pollutant"] == "CH4"

    assert len(first_cell["bbox"]) == 4

    assert first_cell["observed_value"] == pytest.approx(
        1908.4757080078125
    )

    assert first_cell["z_score"] == pytest.approx(
        0.8549911140260236
    )

    assert "severity" in first_cell


def test_get_spatial_no2_cells():
    response = client.get(
        "/api/spatial/cells"
        "?pollutant=NO2"
        "&date=2026-05-09"
    )

    assert response.status_code == 200

    cells = response.json()

    assert len(cells) > 0

    assert all(
        cell["pollutant"] == "NO2"
        for cell in cells
    )


def test_get_spatial_cells_accepts_available_date():
    response = client.get(
        "/api/spatial/cells"
        "?pollutant=NO2"
        "&date=2026-05-10"
    )

    assert response.status_code == 200


def test_spatial_cells_requires_date():
    response = client.get(
        "/api/spatial/cells"
        "?pollutant=CH4"
    )

    assert response.status_code == 422


def test_get_spatial_cells_returns_404_for_unavailable_date():
    response = client.get(
        "/api/spatial/cells"
        "?pollutant=NO2"
        "&date=2026-05-11"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "No cached analysis data available "
            "for 2026-05-11."
        )
    }


def test_get_available_ch4_analysis_dates():
    response = client.get(
        "/api/analysis/dates"
        "?pollutant=CH4"
    )

    assert response.status_code == 200

    assert response.json() == {
        "dates": [
            "2026-05-09",
            "2026-05-10",
        ]
    }


def test_get_available_no2_analysis_dates():
    response = client.get(
        "/api/analysis/dates"
        "?pollutant=NO2"
    )

    assert response.status_code == 200

    assert response.json() == {
        "dates": [
            "2026-05-09",
            "2026-05-10",
        ]
    }
    
def test_get_analysis_coverage():
    response = client.get(
        "/api/analysis/coverage"
        "?pollutant=CH4"
        "&date=2026-05-10"
    )

    assert response.status_code == 200

    assert response.json() == {
        "pollutant": "CH4",
        "date": "2026-05-10",
        "valid_cells": 19,
        "total_cells": 64,
        "coverage_percent": 29.69,
    }


def test_get_analysis_coverage_returns_404_for_missing_date():
    response = client.get(
        "/api/analysis/coverage"
        "?pollutant=CH4"
        "&date=2026-05-11"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "No cached analysis data available "
            "for 2026-05-11."
        )
    }