import json
import os

import requests
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

STATS_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"


load_dotenv()

client_id = os.environ["COPERNICUS_CLIENT_ID"]
client_secret = os.environ["COPERNICUS_CLIENT_SECRET"]

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

token = oauth.fetch_token(
    token_url=TOKEN_URL,
    client_secret=client_secret,
    include_client_id=True,
)


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


evalscript = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: ["NO2", "dataMask"]
        }],
        output: [
            {
                id: "default",
                bands: ["NO2"],
                sampleType: "FLOAT32"
            },
            {
                id: "dataMask",
                bands: 1
            }
        ],
        mosaicking: "ORBIT"
    };
}

function evaluatePixel(samples) {
    let validSamples = samples.filter(sample => sample.dataMask === 1);

    if (validSamples.length === 0) {
        return {
            default: [0],
            dataMask: [0]
        };
    }

    let sum = 0;

    for (let i = 0; i < validSamples.length; i++) {
        sum += validSamples[i].NO2;
    }

    let mean = sum / validSamples.length;

    return {
        default: [mean],
        dataMask: [1]
    };
}
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
                    "minQa": 75
                },
            }
        ],
    },
    "aggregation": {
        "timeRange": {
            "from": "2026-05-01T00:00:00Z",
            "to": "2026-08-11T00:00:00Z",
        },
        "aggregationInterval": {
            "of": "P1D"
        },
        "evalscript": evalscript,
        "resx": 0.05,
        "resy": 0.05,
    },
}

headers = {
    "Authorization": f"Bearer {token['access_token']}",
    "Content-Type": "application/json",
}

response = requests.post(
    STATS_URL,
    headers=headers,
    data=json.dumps(payload),
    timeout=120,
)

print("Status:", response.status_code)

if not response.ok:
    print(response.text)
    raise SystemExit(1)

data = response.json()

with open("stockholm_no2_timeseries.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2)

print("Saved stockholm_no2_timeseries.json")
print("Intervals:", len(data.get("data", [])))