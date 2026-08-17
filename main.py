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

PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"


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

print("Authentication successful.")
print("Token type:", token.get("token_type"))
print("Expires in:", token.get("expires_in"))


# Stockholm / Greater Stockholm
bbox = [17.6, 59.1, 18.5, 59.6]

evalscript = """
//VERSION=3

function setup() {
  return {
    input: ["NO2", "dataMask"],
    output: {
      bands: 2,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [sample.NO2, sample.dataMask];
}
"""

request_payload = {
    "input": {
        "bounds": {
            "bbox": bbox
        },
        "data": [
            {
                "type": "sentinel-5p-l2",
                "dataFilter": {
                    "timeRange": {
                        "from": "2026-08-10T00:00:00Z",
                        "to": "2026-08-10T23:59:59Z"
                    }
                }
            }
        ]
    },
    "output": {
        "width": 512,
        "height": 512,
        "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/tiff"
                }
            }
        ]
    },
    "evalscript": evalscript,
}

headers = {
    "Authorization": f"Bearer {token['access_token']}",
    "Content-Type": "application/json",
}

response = requests.post(
    PROCESS_URL,
    headers=headers,
    data=json.dumps(request_payload),
    timeout=120,
)

print("Status:", response.status_code)
print("Content type:", response.headers.get("content-type"))

if response.ok:
    with open("stockholm_no2.tiff", "wb") as file:
        file.write(response.content)

    print("Saved stockholm_no2.tiff")
else:
    print("Request failed:")
    print(response.text)