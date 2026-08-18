import json

import matplotlib.pyplot as plt
import numpy as np


GRID_SIZE = 8

with open(
    "stockholm_spatial_2026-05-09.json",
    encoding="utf-8",
) as file:
    results = json.load(file)


grid = np.full((GRID_SIZE, GRID_SIZE), np.nan)

for result in results:
    row = result["row"]
    col = result["col"]
    value = result["no2"]

    if value is not None:
        grid[row, col] = value


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
    label="Mean NO₂",
)

plt.scatter(
    max_col,
    max_row,
    marker="x",
    s=150,
    linewidths=3,
    label="Highest NO₂ cell",
)

plt.title(
    "Pollution.ai — Spatial NO₂ Analysis\n"
    "Stockholm, 9 May 2026"
)

plt.xlabel("Grid column")
plt.ylabel("Grid row")

plt.xticks(range(GRID_SIZE))
plt.yticks(range(GRID_SIZE))

plt.legend()
plt.tight_layout()

print(f"Highest cell: row={max_row}, col={max_col}")
print(f"Highest NO2: {max_value:.2e}")

plt.show()