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


def test_get_spatial_anomaly():
    response = client.get("/api/anomalies/spatial")

    assert response.status_code == 200

    assert response.json() == {
        "pollutant": "CH4",
        "date": "2026-05-09",
        "latitude": 59.45,
        "longitude": 18.05,
        "observed_value": 1950.0,
        "baseline_mean": 1880.0,
        "z_score": 3.48,
        "unit": "ppb",
        "severity": "high",
    }
    
