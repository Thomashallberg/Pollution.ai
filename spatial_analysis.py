import json

from copernicus_client import CopernicusClient
from pollutants import POLLUTANTS


# Greater Stockholm
MIN_LON = 17.6
MIN_LAT = 59.1
MAX_LON = 18.5
MAX_LAT = 59.6

GRID_SIZE = 8

POLLUTANT = "CH4"
pollutant_config = POLLUTANTS[POLLUTANT]

ANALYSIS_DATE = "2026-05-09"

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


def build_cells():
    lon_step = (MAX_LON - MIN_LON) / GRID_SIZE
    lat_step = (MAX_LAT - MIN_LAT) / GRID_SIZE

    cells = []

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            min_lon = MIN_LON + col * lon_step
            max_lon = min_lon + lon_step

            min_lat = MIN_LAT + row * lat_step
            max_lat = min_lat + lat_step

            cells.append(
                {
                    "row": row,
                    "col": col,
                    "bbox": [
                        min_lon,
                        min_lat,
                        max_lon,
                        max_lat,
                    ],
                }
            )

    return cells


def get_cell_value(cell):
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
                "from": f"{ANALYSIS_DATE}T00:00:00Z",
                "to": "2026-05-10T00:00:00Z",
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

    if not data.get("data"):
        return None

    stats = (
        data["data"][0]["outputs"]["default"]["bands"][POLLUTANT]["stats"]
    )

    if stats["sampleCount"] == stats["noDataCount"]:
        return None

    return stats["mean"]


cells = build_cells()
results = []

print(
    f"Fetching {POLLUTANT} "
    f"({pollutant_config['label']}) "
    f"for {len(cells)} spatial cells..."
)

for index, cell in enumerate(cells, start=1):
    value = get_cell_value(cell)

    results.append(
        {
            **cell,
            "value": value,
        }
    )

    if index % 8 == 0 or index == len(cells):
        print(f"Processed {index}/{len(cells)} cells")


output_file = (
    f"stockholm_spatial_{POLLUTANT.lower()}_{ANALYSIS_DATE}.json"
)

with open(
    output_file,
    "w",
    encoding="utf-8",
) as file:
    json.dump(results, file, indent=2)

valid_results = [
    result
    for result in results
    if result["value"] is not None
]

print()
print(f"Valid cells: {len(valid_results)}/{len(results)}")

if valid_results:
    highest = max(
        valid_results,
        key=lambda result: result["value"],
    )

    center_lon = (
        highest["bbox"][0] + highest["bbox"][2]
    ) / 2

    center_lat = (
        highest["bbox"][1] + highest["bbox"][3]
    ) / 2

    print(
        f"Highest {POLLUTANT}: "
        f"{highest['value']:.2e} "
        f"{pollutant_config['unit']}"
    )

    print(
        f"Highest cell: row={highest['row']} "
        f"col={highest['col']}"
    )

    print(
        f"Approximate center: "
        f"{center_lat:.4f}, {center_lon:.4f}"
    )

print(f"Saved {output_file}")
print()
print(
    f"Copernicus API requests: "
    f"{copernicus_client.api_requests}"
)

print(
    f"Cache hits: "
    f"{copernicus_client.cache_hits}"
)