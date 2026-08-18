import json

import matplotlib.pyplot as plt
import numpy as np

from pollution_ai.config.pollutants import POLLUTANTS


POLLUTANT = "NO2"
pollutant_config = POLLUTANTS[POLLUTANT]

INPUT_FILE = f"stockholm_{POLLUTANT.lower()}_timeseries.json"

ANOMALY_THRESHOLD = 1.5


with open(INPUT_FILE, encoding="utf-8") as file:
    data = json.load(file)


dates = []
values_list = []

for interval in data["data"]:
    stats = (
        interval["outputs"]["default"]
        ["bands"][POLLUTANT]["stats"]
    )

    if stats["sampleCount"] == stats["noDataCount"]:
        continue

    dates.append(interval["interval"]["from"][:10])
    values_list.append(stats["mean"])


values = np.array(values_list, dtype=float)

if len(values) == 0:
    raise RuntimeError(
        f"No valid {POLLUTANT} observations found."
    )

mean = float(np.mean(values))
std = float(np.std(values))

if std == 0:
    z_scores = np.zeros_like(values)
else:
    z_scores = (values - mean) / std


anomalies = []

for date, value, z_score in zip(
    dates,
    values,
    z_scores,
):
    if z_score >= ANOMALY_THRESHOLD:
        anomalies.append(
            {
                "date": date,
                "value": float(value),
                "z_score": float(z_score),
            }
        )


print()
print(f"Detected {POLLUTANT} anomalies:")
print("----------------------------")

for anomaly in anomalies:
    print(
        f"{anomaly['date']} | "
        f"{POLLUTANT}: "
        f"{anomaly['value']:.2e} "
        f"{pollutant_config['unit']} | "
        f"Z-score: {anomaly['z_score']:.2f}"
    )

print()
print("Intervals returned:", len(data["data"]))
print("Valid observations:", len(values))
print("Minimum:", np.min(values))
print("Maximum:", np.max(values))
print("Mean:", mean)
print("Std:", std)


plt.figure(figsize=(12, 6))

plt.plot(
    dates,
    values,
    marker="o",
    markersize=3,
    label=f"Observed {POLLUTANT}",
)

plt.axhline(
    mean,
    linestyle="--",
    label="Baseline mean",
)

for index, z_score in enumerate(z_scores):
    if z_score >= ANOMALY_THRESHOLD:
        plt.scatter(
            dates[index],
            values[index],
            s=80,
            zorder=5,
        )

plt.title(
    f"Pollution.ai — {pollutant_config['label']} "
    f"Anomaly Detection over Stockholm"
)

plt.xlabel("Date")

plt.ylabel(
    f"Mean {POLLUTANT} "
    f"({pollutant_config['unit']})"
)

plt.xticks(
    range(0, len(dates), 7),
    [
        dates[index]
        for index in range(0, len(dates), 7)
    ],
    rotation=45,
)

plt.legend()
plt.tight_layout()
plt.show()