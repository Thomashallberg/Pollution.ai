import json

import pytest
from fastapi.testclient import TestClient

from pollution_ai.api.app import app


client = TestClient(app)


def build_cell(
    row,
    col,
    observed_value,
    baseline_mean,
    baseline_std,
    z_score,
):
    min_lon = 17.6 + (col * 0.1125)
    min_lat = 59.1 + (row * 0.0625)

    return {
        "row": row,
        "col": col,
        "bbox": [
            min_lon,
            min_lat,
            min_lon + 0.1125,
            min_lat + 0.0625,
        ],
        "pollutant": "",
        "observed_value": observed_value,
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "valid_observations": 10,
        "z_score": z_score,
    }


def write_analysis_file(
    directory,
    pollutant,
    date,
    cells,
):
    for cell in cells:
        cell["pollutant"] = pollutant

    file_path = (
        directory
        / (
            "stockholm_spatial_baseline_"
            f"{pollutant.lower()}_"
            f"{date}.json"
        )
    )

    file_path.write_text(
        json.dumps(cells),
        encoding="utf-8",
    )


@pytest.fixture(autouse=True)
def analysis_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    ch4_2026_05_09 = [
        build_cell(
            row=0,
            col=0,
            observed_value=1908.4757080078125,
            baseline_mean=1891.375,
            baseline_std=20.0,
            z_score=0.8549911140260236,
        ),
        build_cell(
            row=5,
            col=4,
            observed_value=1910.0,
            baseline_mean=1878.0,
            baseline_std=20.0,
            z_score=1.60,
        ),
    ]

    no2_2026_05_09 = [
        build_cell(
            row=0,
            col=0,
            observed_value=0.0001,
            baseline_mean=0.00009,
            baseline_std=0.00001,
            z_score=1.0,
        ),
        build_cell(
            row=2,
            col=3,
            observed_value=0.0002,
            baseline_mean=0.00015,
            baseline_std=0.00001,
            z_score=3.48,
        ),
    ]

    no2_2026_05_10 = [
        build_cell(
            row=0,
            col=0,
            observed_value=0.00012,
            baseline_mean=0.0001,
            baseline_std=0.00001,
            z_score=2.0,
        ),
    ]

    ch4_2026_05_10 = []

    for index in range(64):
        row = index // 8
        col = index % 8

        observed_value = (
            1900.0
            if index < 19
            else None
        )

        ch4_2026_05_10.append(
            build_cell(
                row=row,
                col=col,
                observed_value=observed_value,
                baseline_mean=1880.0,
                baseline_std=20.0,
                z_score=(
                    1.0
                    if observed_value is not None
                    else None
                ),
            )
        )

    write_analysis_file(
        tmp_path,
        "CH4",
        "2026-05-09",
        ch4_2026_05_09,
    )

    write_analysis_file(
        tmp_path,
        "CH4",
        "2026-05-10",
        ch4_2026_05_10,
    )

    write_analysis_file(
        tmp_path,
        "NO2",
        "2026-05-09",
        no2_2026_05_09,
    )

    write_analysis_file(
        tmp_path,
        "NO2",
        "2026-05-10",
        no2_2026_05_10,
    )


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

    assert data["observed_value"] == pytest.approx(
        1910.0
    )

    assert data["baseline_mean"] == pytest.approx(
        1878.0
    )

    assert data["z_score"] == pytest.approx(
        1.60
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
    assert data["z_score"] == pytest.approx(
        3.48
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

    assert len(cells) == 2

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