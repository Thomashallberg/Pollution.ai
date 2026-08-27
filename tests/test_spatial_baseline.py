import pytest

import json


from pollution_ai.analysis.spatial_anomaly_detector import (
    calculate_spatial_z_score,
)
from pollution_ai.analysis.spatial_baseline import (
    build_baseline_lookup,
    run_spatial_baseline,
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
    
def test_run_spatial_baseline_uses_local_files(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    source_file = (
        tmp_path
        / "stockholm_spatial_ch4_2026-05-11.json"
    )

    baseline_file = (
        tmp_path
        / "stockholm_baseline_stats_ch4.json"
    )

    source_file.write_text(
        """
[
    {
        "row": 0,
        "col": 0,
        "bbox": [
            17.6,
            59.1,
            17.7,
            59.2
        ],
        "value": 1900.0
    }
]
""".strip(),
        encoding="utf-8",
    )

    baseline_file.write_text(
        """
[
    {
        "row": 0,
        "col": 0,
        "baseline_mean": 1800.0,
        "baseline_std": 50.0,
        "valid_observations": 30
    }
]
""".strip(),
        encoding="utf-8",
    )

    output_file = run_spatial_baseline(
        pollutant="CH4",
        analysis_date="2026-05-11",
    )

    assert output_file.exists()

    results = json.loads(
        output_file.read_text(
            encoding="utf-8",
        )
    )

    assert len(results) == 1

    result = results[0]

    assert result["pollutant"] == "CH4"
    assert result["observed_value"] == 1900.0
    assert result["baseline_mean"] == 1800.0
    assert result["baseline_std"] == 50.0
    assert result["valid_observations"] == 30
    assert result["z_score"] == pytest.approx(2.0)