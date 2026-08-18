import json

from pollution_ai.integrations.copernicus_client import CopernicusClient
from pollution_ai.config.pollutants import POLLUTANTS


POLLUTANT = "NO2"
pollutant_config = POLLUTANTS[POLLUTANT]

BASELINE_FROM = "2026-05-01T00:00:00Z"
BASELINE_TO = "2026-08-11T00:00:00Z"

copernicus_client = CopernicusClient()


# Greater Stockholm
geometry = {
    "type": "Polygon",
    "coordinates": [
        [
            [17.6, 59.1],
            [18.5, 59.1],
            [18.5, 59.6],
            [17.6, 59.6],
            [17.6, 59.1],
        ]
    ],
}


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

    let mean = sum / validSamples.length;

    return {{
        default: [mean],
        dataMask: [1]
    }};
}}
"""


payload = {
    "input": {
        "bounds": {
            "geometry": geometry,
            "properties": {
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            },
        },
        "data": [
            {
                "type": "sentinel-5p-l2",
                "dataFilter": {
                    "minQa": pollutant_config["min_qa"]
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
            "of": "P1D"
        },
        "evalscript": evalscript,
        "resx": 0.05,
        "resy": 0.05,
    },
}


data = copernicus_client.get_statistics(payload)

output_file = (
    f"stockholm_{POLLUTANT.lower()}_timeseries.json"
)

with open(
    output_file,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        data,
        file,
        indent=2,
    )

print(
    f"Saved {output_file}"
)

print(
    f"Intervals: "
    f"{len(data.get('data', []))}"
)

print()
print(
    f"Copernicus API requests: "
    f"{copernicus_client.api_requests}"
)

print(
    f"Cache hits: "
    f"{copernicus_client.cache_hits}"
)