"""Test bike profile lookups across the v1 and v2 endpoints."""
from typing import Any
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.bosch_ebike.api import BoschEBikeAPI, BoschEBikeAPIError
from custom_components.bosch_ebike.const import (
    API_BASE_URL,
    ENDPOINT_BIKE_PROFILE,
    ENDPOINT_BIKE_PROFILE_V2,
)

GAZELLE = {
    "id": "gazelle-1",
    "brandName": "Gazelle",
    "driveUnit": {"productName": "Active Line Plus"},
    "batteries": [{"batteryLevel": 80}],
}
URBAN_ARROW = {
    "id": "urban-arrow-1",
    "brandName": "Urban Arrow",
    "driveUnit": {"productName": "Performance Line"},
    "batteries": [{"batteryLevel": 55}],
}

V1_GAZELLE = {"id": "gazelle-1", "type": "BikeProfile", "attributes": GAZELLE}


class FakeResponse:
    """Minimal aiohttp response usable as an async context manager."""

    def __init__(self, status: int, body: Any = None) -> None:
        self.status = status
        self._body = body

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=MagicMock(), history=(), status=self.status
            )

    async def json(self) -> Any:
        return self._body


def make_api(routes: dict[str, FakeResponse]) -> tuple[BoschEBikeAPI, list[str]]:
    """Create an API client whose requests are answered from routes by endpoint."""
    requested: list[str] = []

    def request(method: str, url: str, **kwargs: Any) -> FakeResponse:
        endpoint = url.removeprefix(API_BASE_URL)
        requested.append(endpoint)
        return routes.get(endpoint, FakeResponse(404))

    session = MagicMock()
    session.request.side_effect = request
    return BoschEBikeAPI(session, access_token="token"), requested


async def test_get_bikes_lists_all_bikes_from_v2():
    """Test that bikes missing from v1 are found via v2 (issue #35)."""
    api, requested = make_api({
        ENDPOINT_BIKE_PROFILE_V2: FakeResponse(200, [GAZELLE, URBAN_ARROW]),
        ENDPOINT_BIKE_PROFILE: FakeResponse(200, {"data": [V1_GAZELLE]}),
    })

    bikes = await api.get_bikes()

    assert [bike["id"] for bike in bikes] == ["gazelle-1", "urban-arrow-1"]
    assert bikes[1]["attributes"]["brandName"] == "Urban Arrow"
    assert requested == [ENDPOINT_BIKE_PROFILE_V2]


@pytest.mark.parametrize("v2_response", [
    FakeResponse(404),
    FakeResponse(500),
    FakeResponse(200, []),
])
async def test_get_bikes_falls_back_to_v1(v2_response):
    """Test that v1 is used when v2 is missing, failing or empty."""
    api, requested = make_api({
        ENDPOINT_BIKE_PROFILE_V2: v2_response,
        ENDPOINT_BIKE_PROFILE: FakeResponse(200, {"data": [V1_GAZELLE]}),
    })

    bikes = await api.get_bikes()

    assert bikes == [V1_GAZELLE]
    assert requested == [ENDPOINT_BIKE_PROFILE_V2, ENDPOINT_BIKE_PROFILE]


async def test_get_bike_profile_wraps_v2_in_v1_shape():
    """Test that a v2 profile is returned in the v1 shape the coordinator reads."""
    api, requested = make_api({
        f"{ENDPOINT_BIKE_PROFILE_V2}/urban-arrow-1": FakeResponse(200, URBAN_ARROW),
    })

    profile = await api.get_bike_profile("urban-arrow-1")

    assert profile["data"]["id"] == "urban-arrow-1"
    assert profile["data"]["attributes"]["batteries"] == [{"batteryLevel": 55}]
    assert requested == [f"{ENDPOINT_BIKE_PROFILE_V2}/urban-arrow-1"]


async def test_get_bike_profile_falls_back_to_v1():
    """Test that v1 is used when v2 does not know the bike."""
    api, _ = make_api({
        f"{ENDPOINT_BIKE_PROFILE}/gazelle-1": FakeResponse(200, {"data": V1_GAZELLE}),
    })

    assert await api.get_bike_profile("gazelle-1") == {"data": V1_GAZELLE}


async def test_get_bike_profile_reports_v2_error_when_v1_has_no_bike():
    """Test that a v2 failure is raised rather than v1's 404 for a v2-only bike."""
    api, _ = make_api({
        f"{ENDPOINT_BIKE_PROFILE_V2}/urban-arrow-1": FakeResponse(503),
    })

    with pytest.raises(BoschEBikeAPIError):
        await api.get_bike_profile("urban-arrow-1")
