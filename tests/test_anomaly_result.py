from pollution_ai.models.anomaly_result import AnomalyResult


def test_anomaly_result_to_dict():
    result = AnomalyResult(
        pollutant="CH4",
        date="2026-05-09",
        latitude=59.4438,
        longitude=18.1063,
        observed_value=1910.0,
        baseline_mean=1880.0,
        z_score=1.60,
        unit="ppb",
        severity="low",
        deviation_percent=1.7,
    )

    data = result.to_dict()

    assert data == {
        "pollutant": "CH4",
        "date": "2026-05-09",
        "latitude": 59.4438,
        "longitude": 18.1063,
        "observed_value": 1910.0,
        "baseline_mean": 1880.0,
        "z_score": 1.60,
        "unit": "ppb",
        "severity": "low",
        "deviation_percent": 1.7,
    }