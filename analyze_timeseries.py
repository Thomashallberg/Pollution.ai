import json

import matplotlib.pyplot as plt
import numpy as np


with open("stockholm_no2_timeseries.json", encoding="utf-8") as file:
    data = json.load(file)


dates = []
means = []

for interval in data["data"]:
    stats = interval["outputs"]["default"]["bands"]["NO2"]["stats"]

    if stats["sampleCount"] == stats["noDataCount"]:
        continue

    dates.append(interval["interval"]["from"][:10])
    means.append(stats["mean"])


values = np.array(means, dtype=float)

mean = np.mean(values)
std = np.std(values)

z_scores = (values - mean) / std

threshold = 1.5

anomalies = []

for date, value, z_score in zip(dates, values, z_scores):
    if z_score >= threshold:
        anomalies.append(
            {
                "date": date,
                "no2": value,
                "z_score": z_score,
            }
        )

print("\nDetected anomalies:")
print("-------------------")

for anomaly in anomalies:
    print(
        f"{anomaly['date']} | "
        f"NO2: {anomaly['no2']:.2e} | "
        f"Z-score: {anomaly['z_score']:.2f}"
    )

print("Intervals returned:", len(data["data"]))
print("Valid observations:", len(values))

print("Minimum:", np.min(values))
print("Maximum:", np.max(values))
print("Mean:", np.mean(values))
print("Std:", np.std(values))


plt.figure(figsize=(12, 6))

plt.plot(
    dates,
    values,
    marker="o",
    markersize=3,
    label="Observed NO₂",
)

plt.axhline(
    mean,
    linestyle="--",
    label="Baseline mean",
)

for i, z_score in enumerate(z_scores):
    if z_score >= threshold:
        plt.scatter(
            dates[i],
            values[i],
            s=80,
            zorder=5,
        )

plt.title("Pollution.ai — NO₂ Anomaly Detection over Stockholm")
plt.xlabel("Date")
plt.ylabel("Mean NO₂")

plt.xticks(
    range(0, len(dates), 7),
    [dates[i] for i in range(0, len(dates), 7)],
    rotation=45,
)

plt.legend()
plt.tight_layout()
plt.show()