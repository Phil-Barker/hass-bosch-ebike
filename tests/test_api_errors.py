"""Test API error handling for optional endpoints."""
import asyncio
import logging
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.bosch_ebike.api import BoschEBikeAPI, BoschEBikeAPIError


def make_api(side_effect):
    """Create an API client whose requests fail with side_effect."""
    session = MagicMock()
    session.request.side_effect = side_effect
    return BoschEBikeAPI(session, access_token="token")


async def test_timeout_raises_api_error():
    """Test that a timeout is reported as an API error, not an unhandled exception."""
    api = make_api(asyncio.TimeoutError())

    with pytest.raises(BoschEBikeAPIError):
        await api.get_bike_profile("bike-1")


async def test_location_unavailable_is_quiet(caplog):
    """Test that a rejected location request returns None without logging errors."""
    forbidden = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=403
    )
    api = make_api(forbidden)

    with caplog.at_level(logging.DEBUG):
        assert await api.get_latest_location("bike-1") is None

    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]


async def test_location_timeout_returns_none():
    """Test that a location timeout does not fail the whole update."""
    api = make_api(asyncio.TimeoutError())

    assert await api.get_latest_location("bike-1") is None
