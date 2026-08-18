import json

import matplotlib.pyplot as plt
import numpy as np

from pollution_ai.config.pollutants import POLLUTANTS


GRID_SIZE = 8

POLLUTANT = "CH4"
pollutant_config = POLLUTANTS[POLLUTANT]

ANALYSIS_DATE = "2026-05-09"

INPUT_FILE = (
    f"stockholm_spatial_"
    f"{POLLUTANT.lower()}_"
    f"{ANALYSIS_DATE}.json"
)


with open(
    INPUT_FILE,
    encoding="utf-8",
) as file:
    results = json.load(file)


grid = np.full(
    (GRID_SIZE, GRID_SIZE),
    np.nan,
)

for result in results:
    row = result["row"]
    col = result["col"]
    value = result["value"]

    if value is not None:
        grid[row, col] = value


if np.all(np.isnan(grid)):
    raise RuntimeError(
        f"No valid {POLLUTANT} spatial values found."
    )


max_index = np.nanargmax(grid)

max_row, max_col = np.unravel_index(
    max_index,
    grid.shape,
)

max_value = grid[max_row, max_col]


plt.figure(figsize=(9, 7))

image = plt.imshow(
    grid,
    origin="lower",
)

plt.colorbar(
    image,
    label=(
        f"Mean {POLLUTANT} "
        f"({pollutant_config['unit']})"
    ),
)

plt.scatter(
    max_col,
    max_row,
    marker="x",
    s=150,
    linewidths=3,
    label=f"Highest {POLLUTANT} cell",
)

plt.title(
    f"Pollution.ai — Spatial "
    f"{pollutant_config['label']} Analysis\n"
    f"Stockholm, {ANALYSIS_DATE}"
)

plt.xlabel("Grid column")
plt.ylabel("Grid row")

plt.xticks(range(GRID_SIZE))
plt.yticks(range(GRID_SIZE))

plt.legend()
plt.tight_layout()

print(
    f"Highest cell: "
    f"row={max_row}, col={max_col}"
)

print(
    f"Highest {POLLUTANT}: "
    f"{max_value:.2e} "
    f"{pollutant_config['unit']}"
)

plt.show()