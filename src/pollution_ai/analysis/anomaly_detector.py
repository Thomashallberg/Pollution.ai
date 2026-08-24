import numpy as np


def calculate_z_scores(values):
    values = np.asarray(values, dtype=float)

    if len(values) == 0:
        raise ValueError("Values cannot be empty.")

    mean = float(np.mean(values))
    std = float(np.std(values))

    if std == 0:
        z_scores = np.zeros_like(values)
    else:
        z_scores = (values - mean) / std

    return mean, std, z_scores


def detect_anomalies(
    dates,
    values,
    z_scores,
    threshold=1.5,
):
    anomalies = []

    for date, value, z_score in zip(
        dates,
        values,
        z_scores,
    ):
        if z_score >= threshold:
            anomalies.append(
                {
                    "date": date,
                    "value": float(value),
                    "z_score": float(z_score),
                }
            )

    return anomalies


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