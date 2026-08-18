import hashlib
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

STATS_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"


class CopernicusClient:
    def __init__(
        self,
        max_retries: int = 5,
        request_delay: float = 0.3,
        cache_dir: str = "cache",
    ) -> None:
        load_dotenv()

        self.client_id = os.environ["COPERNICUS_CLIENT_ID"]
        self.client_secret = os.environ["COPERNICUS_CLIENT_SECRET"]

        self.max_retries = max_retries
        self.request_delay = request_delay

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._access_token: str | None = None

        self.api_requests = 0
        self.cache_hits = 0

    def authenticate(self) -> None:
        client = BackendApplicationClient(
            client_id=self.client_id,
        )

        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(
            token_url=TOKEN_URL,
            client_secret=self.client_secret,
            include_client_id=True,
        )

        self._access_token = token["access_token"]

    def _build_cache_key(self, payload: dict) -> str:
        serialized_payload = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            serialized_payload.encode("utf-8")
        ).hexdigest()

    def _get_cache_path(self, payload: dict) -> Path:
        cache_key = self._build_cache_key(payload)

        return self.cache_dir / f"{cache_key}.json"

    def _load_cache(self, payload: dict) -> dict | None:
        cache_path = self._get_cache_path(payload)

        if not cache_path.exists():
            return None

        with cache_path.open(
            encoding="utf-8",
        ) as file:
            cached_data = json.load(file)

        self.cache_hits += 1

        return cached_data

    def _save_cache(
        self,
        payload: dict,
        data: dict,
    ) -> None:
        cache_path = self._get_cache_path(payload)

        with cache_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
            )

    def get_statistics(
        self,
        payload: dict,
        use_cache: bool = True,
    ) -> dict:
        if use_cache:
            cached_data = self._load_cache(payload)

            if cached_data is not None:
                return cached_data

        if self._access_token is None:
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        for attempt in range(self.max_retries):
            response = requests.post(
                STATS_URL,
                headers=headers,
                json=payload,
                timeout=120,
            )

            if response.status_code == 429:
                retry_after_ms = int(
                    response.headers.get(
                        "Retry-After",
                        "2000",
                    )
                )

                wait_seconds = retry_after_ms / 1000

                print(
                    f"Rate limited. Waiting "
                    f"{wait_seconds:.1f}s "
                    f"(attempt "
                    f"{attempt + 1}/{self.max_retries})..."
                )

                time.sleep(wait_seconds)
                continue

            if response.status_code == 401:
                self._access_token = None

                if attempt < self.max_retries - 1:
                    self.authenticate()
                    continue

            response.raise_for_status()

            data = response.json()

            self.api_requests += 1

            if use_cache:
                self._save_cache(
                    payload,
                    data,
                )

            time.sleep(self.request_delay)

            return data

        raise RuntimeError(
            "Copernicus request failed after maximum retries."
        )