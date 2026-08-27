import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from pollution_ai.config.pollutants import POLLUTANTS
from pollution_ai.integrations.copernicus_client import CopernicusClient


# Greater Stockholm
MIN_LON = 17.6
MIN_LAT = 59.1
MAX_LON = 18.5
MAX_LAT = 59.6

GRID_SIZE = 8


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Fetch spatial Copernicus pollution data "
            "for Greater Stockholm."
        )
    )

    parser.add_argument(
        "--pollutant",
        choices=POLLUTANTS.keys(),
        required=True,
        help="Pollutant to analyse.",
    )

    parser.add_argument(
        "--date",
        required=True,
        help="Analysis date in YYYY-MM-DD format.",
    )

    return parser.parse_args()


def parse_analysis_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            "Date must use YYYY-MM-DD format."
        ) from error


def build_evalscript(pollutant: str) -> str:
    return f"""
//VERSION=3

function setup() {{
    return {{
        input: [{{
            bands: ["{pollutant}", "dataMask"]
        }}],
        output: [
            {{
                id: "default",
                bands: ["{pollutant}"],
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
    let validSamples = samples.filter(
        sample => sample.dataMask === 1
    );

    if (validSamples.length === 0) {{
        return {{
            default: [0],
            dataMask: [0]
        }};
    }}

    let sum = 0;

    for (
        let i = 0;
        i < validSamples.length;
        i++
    ) {{
        sum += validSamples[i].{pollutant};
    }}

    return {{
        default: [
            sum / validSamples.length
        ],
        dataMask: [1]
    }};
}}
"""


def build_cells():
    lon_step = (
        MAX_LON - MIN_LON
    ) / GRID_SIZE

    lat_step = (
        MAX_LAT - MIN_LAT
    ) / GRID_SIZE

    cells = []

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            min_lon = (
                MIN_LON + col * lon_step
            )

            max_lon = (
                min_lon + lon_step
            )

            min_lat = (
                MIN_LAT + row * lat_step
            )

            max_lat = (
                min_lat + lat_step
            )

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


def get_cell_value(
    cell,
    pollutant,
    pollutant_config,
    analysis_date,
    next_date,
    evalscript,
    copernicus_client,
):
    payload = {
        "input": {
            "bounds": {
                "bbox": cell["bbox"],
            },
            "data": [
                {
                    "type": "sentinel-5p-l2",
                    "dataFilter": {
                        "minQa": (
                            pollutant_config[
                                "min_qa"
                            ]
                        ),
                    },
                }
            ],
        },
        "aggregation": {
            "timeRange": {
                "from": (
                    f"{analysis_date}"
                    "T00:00:00Z"
                ),
                "to": (
                    f"{next_date}"
                    "T00:00:00Z"
                ),
            },
            "aggregationInterval": {
                "of": "P1D",
            },
            "evalscript": evalscript,
            "resx": 0.02,
            "resy": 0.02,
        },
    }

    data = (
        copernicus_client
        .get_statistics(payload)
    )

    if not data.get("data"):
        return None

    stats = (
        data["data"][0]
        ["outputs"]["default"]
        ["bands"][pollutant]["stats"]
    )

    if (
        stats["sampleCount"]
        == stats["noDataCount"]
    ):
        return None

    return stats["mean"]


def run_spatial_analysis(
    pollutant: str,
    analysis_date: str,
    copernicus_client=None,
) -> Path:
    if pollutant not in POLLUTANTS:
        raise ValueError(
            f"Unsupported pollutant: {pollutant}"
        )

    analysis_date_value = (
        parse_analysis_date(
            analysis_date
        )
    )

    analysis_date = (
        analysis_date_value.isoformat()
    )

    next_date = (
        analysis_date_value
        + timedelta(days=1)
    ).isoformat()

    pollutant_config = (
        POLLUTANTS[pollutant]
    )

    if copernicus_client is None:
        copernicus_client = (
            CopernicusClient()
        )

    evalscript = build_evalscript(
        pollutant
    )

    cells = build_cells()
    results = []

    print(
        f"Fetching {pollutant} "
        f"({pollutant_config['label']}) "
        f"for {analysis_date} "
        f"across {len(cells)} "
        f"spatial cells..."
    )

    for index, cell in enumerate(
        cells,
        start=1,
    ):
        value = get_cell_value(
            cell=cell,
            pollutant=pollutant,
            pollutant_config=(
                pollutant_config
            ),
            analysis_date=analysis_date,
            next_date=next_date,
            evalscript=evalscript,
            copernicus_client=(
                copernicus_client
            ),
        )

        results.append(
            {
                **cell,
                "value": value,
            }
        )

        if (
            index % 8 == 0
            or index == len(cells)
        ):
            print(
                f"Processed "
                f"{index}/{len(cells)} cells"
            )

    output_file = Path(
        "stockholm_spatial_"
        f"{pollutant.lower()}_"
        f"{analysis_date}.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    valid_results = [
        result
        for result in results
        if result["value"] is not None
    ]

    print()

    print(
        f"Valid cells: "
        f"{len(valid_results)}/"
        f"{len(results)}"
    )

    if valid_results:
        highest = max(
            valid_results,
            key=lambda result: (
                result["value"]
            ),
        )

        center_lon = (
            highest["bbox"][0]
            + highest["bbox"][2]
        ) / 2

        center_lat = (
            highest["bbox"][1]
            + highest["bbox"][3]
        ) / 2

        print(
            f"Highest {pollutant}: "
            f"{highest['value']:.2e} "
            f"{pollutant_config['unit']}"
        )

        print(
            f"Highest cell: "
            f"row={highest['row']} "
            f"col={highest['col']}"
        )

        print(
            "Approximate center: "
            f"{center_lat:.4f}, "
            f"{center_lon:.4f}"
        )

    print(
        f"Saved {output_file}"
    )

    print()

    print(
        "Copernicus API requests: "
        f"{copernicus_client.api_requests}"
    )

    print(
        "Cache hits: "
        f"{copernicus_client.cache_hits}"
    )

    return output_file


def main():
    args = parse_arguments()

    run_spatial_analysis(
        pollutant=args.pollutant,
        analysis_date=args.date,
    )


if __name__ == "__main__":
    main()