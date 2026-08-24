from pollution_ai.analysis.anomaly_detector import classify_severity
from pollution_ai.models.anomaly_result import AnomalyResult


def build_anomaly_result(
    strongest,
    pollutant,
    date,
    unit,
):
    if strongest is None:
        return None

    center_lon = (
        strongest["bbox"][0]
        + strongest["bbox"][2]
    ) / 2

    center_lat = (
        strongest["bbox"][1]
        + strongest["bbox"][3]
    ) / 2

    return AnomalyResult(
        pollutant=pollutant,
        date=date,
        latitude=center_lat,
        longitude=center_lon,
        observed_value=strongest["observed_value"],
        baseline_mean=strongest["baseline_mean"],
        z_score=strongest["z_score"],
        unit=unit,
        severity=classify_severity(strongest["z_score"]),
    )

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
    
def classify_severity(z_score):
    if z_score is None:
        return None

    if z_score >= 4.0:
        return "extreme"

    if z_score >= 3.0:
        return "high"

    if z_score >= 2.0:
        return "moderate"

    return "low"