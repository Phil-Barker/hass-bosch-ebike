"""Bike picture for the Bosch eBike integration.

The bike picture from the Bosch bike profile is a wide side view. Home
Assistant shows entity pictures as circles cropped with "cover", so only the
middle of the bike would be visible. This module serves a square version of
the picture with the whole bike scaled to fit inside that circle.
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import logging

from aiohttp import ClientError, web
import async_timeout
from PIL import Image

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PICTURE_URL = "/api/bosch_ebike/picture/{bike_id}"
PICTURE_SIZE = 256
# Leave a small margin so the bike does not touch the marker border
PICTURE_FILL = 0.92


def picture_path(bike_id: str, source_url: str) -> str:
    """Return the local picture URL, versioned by the source picture."""
    version = hashlib.sha256(source_url.encode()).hexdigest()[:8]
    return f"{PICTURE_URL.format(bike_id=bike_id)}?v={version}"


def fit_picture_in_circle(data: bytes, size: int = PICTURE_SIZE) -> bytes:
    """Scale a picture so it fits entirely inside a circle of the given size."""
    with Image.open(io.BytesIO(data)) as source:
        image = source.convert("RGBA")

    # Trim transparent margins around the bike
    bbox = image.getchannel("A").getbbox()
    if bbox:
        image = image.crop(bbox)

    # A rectangle fits inside a circle when its diagonal fits the diameter
    width, height = image.size
    scale = size * PICTURE_FILL / (width**2 + height**2) ** 0.5
    image = image.resize(
        (max(1, round(width * scale)), max(1, round(height * scale))),
        Image.Resampling.LANCZOS,
    )

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))

    output = io.BytesIO()
    canvas.save(output, format="PNG", optimize=True)
    return output.getvalue()


class BoschEBikePictureView(HomeAssistantView):
    """Serve the bike picture scaled to fit a round entity picture."""

    name = "api:bosch_ebike:picture"
    url = PICTURE_URL
    # Entity pictures are loaded by the browser without an auth header. The
    # picture is the public model picture from the Bosch CDN, and only
    # configured bike IDs are served.
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the view."""
        self.hass = hass
        self._cache: dict[str, bytes] = {}

    def _get_source_url(self, bike_id: str) -> str | None:
        """Return the Bosch picture URL of a configured bike."""
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if entry_data.get("bike_id") != bike_id:
                continue
            data = entry_data["coordinator"].data or {}
            return data.get("bike", {}).get("picture_url")
        return None

    async def get(self, request: web.Request, bike_id: str) -> web.Response:
        """Return the scaled bike picture."""
        source_url = self._get_source_url(bike_id)
        if not source_url:
            raise web.HTTPNotFound

        if source_url not in self._cache:
            session = async_get_clientsession(self.hass)
            try:
                async with async_timeout.timeout(30):
                    async with session.get(source_url) as response:
                        response.raise_for_status()
                        data = await response.read()
                picture = await self.hass.async_add_executor_job(
                    fit_picture_in_circle, data
                )
            except (ClientError, asyncio.TimeoutError, OSError, ValueError) as err:
                _LOGGER.warning("Failed to load bike picture %s: %s", source_url, err)
                raise web.HTTPBadGateway from err
            self._cache[source_url] = picture

        return web.Response(
            body=self._cache[source_url],
            content_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )
