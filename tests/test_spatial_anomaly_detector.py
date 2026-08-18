from pollution_ai.analysis.spatial_anomaly_detector import (
    calculate_spatial_z_score,
    find_strongest_spatial_anomaly,
)


def test_calculate_spatial_z_score():
    z_score = calculate_spatial_z_score(
        observed_value=4.3,
        baseline_mean=1.9,
        baseline_std=0.69,
    )

    assert round(z_score, 2) == 3.48


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

    assert strongest["row"] == 4
    assert strongest["col"] == 3
    assert strongest["z_score"] == 3.48