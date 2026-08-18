import json
from unittest.mock import Mock, patch

from pollution_ai.integrations.copernicus_client import CopernicusClient


def test_cache_hit_returns_cached_data_without_api_request(tmp_path):
    client = CopernicusClient(
        cache_dir=str(tmp_path),
    )

    payload = {
        "test": "pollution-ai",
    }

    expected_data = {
        "data": [
            {
                "value": 123,
            }
        ]
    }

    cache_path = client._get_cache_path(payload)

    with cache_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            expected_data,
            file,
        )

    result = client.get_statistics(payload)

    assert result == expected_data
    assert client.cache_hits == 1
    assert client.api_requests == 0


def test_cache_miss_calls_api_and_saves_response(tmp_path):
    client = CopernicusClient(
        cache_dir=str(tmp_path),
        request_delay=0,
    )

    payload = {
        "test": "cache-miss",
    }

    expected_data = {
        "data": [
            {
                "value": 456,
            }
        ]
    }

    response = Mock()
    response.status_code = 200
    response.json.return_value = expected_data
    response.raise_for_status.return_value = None

    client._access_token = "fake-token"

    with patch(
        "pollution_ai.integrations.copernicus_client.requests.post",
        return_value=response,
    ) as mock_post:
        result = client.get_statistics(payload)

    assert result == expected_data
    assert client.api_requests == 1
    assert client.cache_hits == 0
    assert mock_post.call_count == 1

    cache_path = client._get_cache_path(payload)

    assert cache_path.exists()

    with cache_path.open(
        encoding="utf-8",
    ) as file:
        cached_data = json.load(file)

    assert cached_data == expected_data


def test_rate_limit_retries_and_succeeds(tmp_path):
    client = CopernicusClient(
        cache_dir=str(tmp_path),
        request_delay=0,
        max_retries=3,
    )

    payload = {
        "test": "rate-limit",
    }

    rate_limited_response = Mock()
    rate_limited_response.status_code = 429
    rate_limited_response.headers = {
        "Retry-After": "100",
    }

    expected_data = {
        "data": [
            {
                "value": 789,
            }
        ]
    }

    successful_response = Mock()
    successful_response.status_code = 200
    successful_response.json.return_value = expected_data
    successful_response.raise_for_status.return_value = None

    client._access_token = "fake-token"

    with (
        patch(
            "pollution_ai.integrations.copernicus_client.requests.post",
            side_effect=[
                rate_limited_response,
                successful_response,
            ],
        ) as mock_post,
        patch(
            "pollution_ai.integrations.copernicus_client.time.sleep",
        ) as mock_sleep,
    ):
        result = client.get_statistics(payload)

    assert result == expected_data
    assert mock_post.call_count == 2
    assert mock_sleep.call_count == 2
    assert client.api_requests == 1
    assert client.cache_hits == 0


def test_unauthorized_reauthenticates_and_retries(tmp_path):
    client = CopernicusClient(
        cache_dir=str(tmp_path),
        request_delay=0,
        max_retries=3,
    )

    payload = {
        "test": "unauthorized",
    }

    unauthorized_response = Mock()
    unauthorized_response.status_code = 401

    expected_data = {
        "data": [
            {
                "value": 999,
            }
        ]
    }

    successful_response = Mock()
    successful_response.status_code = 200
    successful_response.json.return_value = expected_data
    successful_response.raise_for_status.return_value = None

    client._access_token = "expired-token"

    with (
        patch(
            "pollution_ai.integrations.copernicus_client.requests.post",
            side_effect=[
                unauthorized_response,
                successful_response,
            ],
        ) as mock_post,
        patch.object(
            client,
            "authenticate",
        ) as mock_authenticate,
    ):
        mock_authenticate.side_effect = lambda: setattr(
            client,
            "_access_token",
            "new-token",
        )

        result = client.get_statistics(payload)

    assert result == expected_data
    assert mock_post.call_count == 2
    assert mock_authenticate.call_count == 1
    assert client.api_requests == 1
    assert client.cache_hits == 0