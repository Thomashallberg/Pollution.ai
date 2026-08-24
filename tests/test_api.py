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
        "/api/anomalies/spatial?pollutant=CH4"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pollutant"] == "CH4"
    assert data["date"] == "2026-05-09"
    assert data["unit"] == "ppb"

    assert data["latitude"] == pytest.approx(59.44375)
    assert data["longitude"] == pytest.approx(18.10625)

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
        "/api/anomalies/spatial?pollutant=NO2"
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
        "/api/anomalies/spatial?pollutant=banana"
    )

    assert response.status_code == 422