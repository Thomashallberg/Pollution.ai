import json
from pathlib import Path

import numpy as np

from copernicus_client import CopernicusClient
from pollutants import POLLUTANTS


POLLUTANT = "CH4"
pollutant_config = POLLUTANTS[POLLUTANT]

ANALYSIS_DATE = "2026-05-09"

SOURCE_FILE = (
    f"stockholm_spatial_{POLLUTANT.lower()}_{ANALYSIS_DATE}.json"
)

OUTPUT_FILE = Path(
    f"stockholm_spatial_baseline_{POLLUTANT.lower()}.json"
)

BASELINE_FROM = "2026-05-01T00:00:00Z"
BASELINE_TO = "2026-08-11T00:00:00Z"

copernicus_client = CopernicusClient()


evalscript = f"""
//VERSION=3

function setup() {{
    return {{
        input: [{{
            bands: ["{POLLUTANT}", "dataMask"]
        }}],
        output: [
            {{
                id: "default",
                bands: ["{POLLUTANT}"],
                sampleType: "FLOAT32"
            }},
            {{
                id: "dataMask",
                bands: 1
            }}
        ],
        mosaicking: "ORBIT"
    }};
}}

function evaluatePixel(samples) {{
    let validSamples = samples.filter(sample => sample.dataMask === 1);

    if (validSamples.length === 0) {{
        return {{
            default: [0],
            dataMask: [0]
        }};
    }}

    let sum = 0;

    for (let i = 0; i < validSamples.length; i++) {{
        sum += validSamples[i].{POLLUTANT};
    }}

    return {{
        default: [sum / validSamples.length],
        dataMask: [1]
    }};
}}
"""


def load_existing_results():
    if not OUTPUT_FILE.exists():
        return []

    with OUTPUT_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def save_results(results):
    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )


def get_cell_history(cell):
    payload = {
        "input": {
            "bounds": {
                "bbox": cell["bbox"],
            },
            "data": [
                {
                    "type": "sentinel-5p-l2",
                    "dataFilter": {
                        "minQa": pollutant_config["min_qa"],
                    },
                }
            ],
        },
        "aggregation": {
            "timeRange": {
                "from": BASELINE_FROM,
                "to": BASELINE_TO,
            },
            "aggregationInterval": {
                "of": "P1D",
            },
            "evalscript": evalscript,
            "resx": 0.02,
            "resy": 0.02,
        },
    }

    data = copernicus_client.get_statistics(payload)

    values = []

    for interval in data.get("data", []):
        stats = (
            interval["outputs"]["default"]
            ["bands"][POLLUTANT]["stats"]
        )

        if stats["sampleCount"] == stats["noDataCount"]:
            continue

        values.append(stats["mean"])

    return values


with open(SOURCE_FILE, encoding="utf-8") as file:
    spatial_cells = json.load(file)


results = load_existing_results()

completed_cells = {
    (result["row"], result["col"])
    for result in results
}

print(
    f"Existing {POLLUTANT} baseline cells: "
    f"{len(completed_cells)}/{len(spatial_cells)}"
)


for cell in spatial_cells:
    key = (cell["row"], cell["col"])

    if key in completed_cells:
        continue

    history = get_cell_history(cell)

    observed = cell["value"]

    if history:
        values = np.array(
            history,
            dtype=float,
        )

        mean = float(np.mean(values))
        std = float(np.std(values))

        if observed is not None and std > 0:
            z_score = float(
                (observed - mean) / std
            )
        else:
            z_score = None

        result = {
            "row": cell["row"],
            "col": cell["col"],
            "bbox": cell["bbox"],
            "pollutant": POLLUTANT,
            "observed_value": observed,
            "baseline_mean": mean,
            "baseline_std": std,
            "valid_observations": len(values),
            "z_score": z_score,
        }

    else:
        result = {
            "row": cell["row"],
            "col": cell["col"],
            "bbox": cell["bbox"],
            "pollutant": POLLUTANT,
            "observed_value": observed,
            "baseline_mean": None,
            "baseline_std": None,
            "valid_observations": 0,
            "z_score": None,
        }

    results.append(result)

    save_results(results)

    if (
        len(results) % 8 == 0
        or len(results) == len(spatial_cells)
    ):
        print(
            f"Processed "
            f"{len(results)}/{len(spatial_cells)} cells"
        )


valid_results = [
    result
    for result in results
    if result["z_score"] is not None
]

print()
print(
    f"Valid {POLLUTANT} baseline cells: "
    f"{len(valid_results)}/{len(results)}"
)

if valid_results:
    strongest = max(
        valid_results,
        key=lambda result: result["z_score"],
    )

    center_lon = (
        strongest["bbox"][0]
        + strongest["bbox"][2]
    ) / 2

    center_lat = (
        strongest["bbox"][1]
        + strongest["bbox"][3]
    ) / 2

    print(
        f"Strongest {POLLUTANT} spatial anomaly: "
        f"row={strongest['row']} "
        f"col={strongest['col']}"
    )

    print(
        f"Observed {POLLUTANT}: "
        f"{strongest['observed_value']:.2e} "
        f"{pollutant_config['unit']}"
    )

    print(
        f"Baseline mean: "
        f"{strongest['baseline_mean']:.2e} "
        f"{pollutant_config['unit']}"
    )

    print(
        f"Z-score: "
        f"{strongest['z_score']:.2f}"
    )

    print(
        f"Approximate center: "
        f"{center_lat:.4f}, {center_lon:.4f}"
    )

print(f"Saved {OUTPUT_FILE}")

print()
print(
    f"Copernicus API requests: "
    f"{copernicus_client.api_requests}"
)
print(
    f"Cache hits: "
    f"{copernicus_client.cache_hits}"
)