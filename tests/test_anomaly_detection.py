import numpy as np
import pytest

from pollution_ai.analysis.anomaly_detector import (
    calculate_z_scores,
    detect_anomalies,
)


def test_calculate_z_scores_returns_expected_values():
    values = [1, 2, 3]

    mean, std, z_scores = calculate_z_scores(values)

    assert mean == 2.0
    assert np.isclose(std, np.std(values))

    expected = np.array([-1.22474487, 0.0, 1.22474487])

    assert np.allclose(z_scores, expected)


def test_calculate_z_scores_handles_zero_standard_deviation():
    values = [5, 5, 5]

    mean, std, z_scores = calculate_z_scores(values)

    assert mean == 5.0
    assert std == 0.0
    assert np.allclose(z_scores, [0.0, 0.0, 0.0])


def test_calculate_z_scores_rejects_empty_values():
    with pytest.raises(ValueError, match="Values cannot be empty"):
        calculate_z_scores([])
        
def test_detect_anomalies_returns_values_above_threshold():
    dates = [
        "2026-05-01",
        "2026-05-02",
        "2026-05-03",
    ]

    values = [10, 20, 30]
    z_scores = [0.2, 1.6, 2.4]

    anomalies = detect_anomalies(
        dates,
        values,
        z_scores,
        threshold=1.5,
    )

    assert len(anomalies) == 2

    assert anomalies[0]["date"] == "2026-05-02"
    assert anomalies[0]["value"] == 20.0
    assert anomalies[0]["z_score"] == 1.6

    assert anomalies[1]["date"] == "2026-05-03"
    assert anomalies[1]["value"] == 30.0
    assert anomalies[1]["z_score"] == 2.4