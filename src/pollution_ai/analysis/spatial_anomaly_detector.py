def calculate_spatial_z_score(
    observed_value,
    baseline_mean,
    baseline_std,
):
    if observed_value is None:
        return None

    if baseline_mean is None:
        return None

    if baseline_std is None or baseline_std <= 0:
        return None

    return float(
        (observed_value - baseline_mean)
        / baseline_std
    )


def find_strongest_spatial_anomaly(results):
    valid_results = [
        result
        for result in results
        if result.get("z_score") is not None
    ]

    if not valid_results:
        return None

    return max(
        valid_results,
        key=lambda result: result["z_score"],
    )