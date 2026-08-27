import pytest

from pollution_ai.analysis.spatial_anomaly_detector import (
    calculate_spatial_z_score,
)
from pollution_ai.analysis.spatial_baseline import (
    build_baseline_lookup,
)


def test_build_baseline_lookup_and_calculate_z_score():
    baseline_stats = [
        {
            "row": 0,
            "col": 0,
            "bbox": [
                17.6,
                59.1,
                17.7125,
                59.1625,
            ],
            "pollutant": "CH4",
            "baseline_mean": 1891.2584451342386,
            "baseline_std": 20.137358846339808,
            "valid_observations": 7,
        }
    ]

    lookup = build_baseline_lookup(
        baseline_stats
    )

    baseline = lookup[(0, 0)]

    observed_value = 1908.4757080078125

    z_score = calculate_spatial_z_score(
        observed_value=observed_value,
        baseline_mean=baseline["baseline_mean"],
        baseline_std=baseline["baseline_std"],
    )

    assert baseline["valid_observations"] == 7

    assert z_score == pytest.approx(
        0.8549911140260236
    )