"""Config flow for Bosch eBike integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult

from .api import BoschEBikeAPI, BoschEBikeAuthError, BoschEBikeAPIError
from .const import (
    DOMAIN,
    CONF_BIKE_ID,
    CONF_BIKE_NAME,
)

_LOGGER = logging.getLogger(__name__)

CONF_CODE = "code"
CONF_CODE_VERIFIER = "code_verifier"
CONF_REFRESH_TOKEN = "refresh_token"


def _build_bike_name(bike: dict[str, Any]) -> str:
    """Build a descriptive bike name from bike data."""
    attrs = bike.get("attributes", {})
    brand_name = attrs.get("brandName", "eBike")
    drive_unit = attrs.get("driveUnit", {})
    drive_unit_name = drive_unit.get("productName")

    # Try to get frame number for uniqueness
    frame_number = attrs.get("frameNumber")

    if drive_unit_name:
        # e.g., "Cube (Performance CX)"
        return f"{brand_name} ({drive_unit_name})"
    elif frame_number and len(frame_number) >= 4:
        # e.g., "Cube (...1234)" - last 4 digits of frame number
        return f"{brand_name} (...{frame_number[-4:]})"
    else:
        # Just the brand name
        return brand_name


class BoschEBikeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bosch eBike."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._code_verifier: str | None = None
        self._code_challenge: str | None = None
        self._bikes: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Generate PKCE parameters
        self._code_verifier, self._code_challenge = BoschEBikeAPI.generate_pkce_pair()

        # Build authorization URL
        auth_url = BoschEBikeAPI.build_auth_url(self._code_challenge)

        # Store for next step
        self.context["code_verifier"] = self._code_verifier

        # Show auth URL and ask for code manually
        return self.async_show_form(
            step_id="auth",
            description_placeholders={"auth_url": auth_url},
            data_schema=vol.Schema({
                vol.Required(CONF_CODE): str,
            }),
        )

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual authorization code entry."""
        if user_input is None:
            return self.async_abort(reason="missing_code")

        # Extract authorization code from user input
        authorization_code = user_input[CONF_CODE].strip()

        # Get code_verifier from context
        code_verifier = self.context.get("code_verifier")
        if not code_verifier:
            return self.async_abort(reason="missing_verifier")

        errors = {}

        try:
            # Exchange code for tokens
            session = async_get_clientsession(self.hass)
            api = BoschEBikeAPI(session)

            token_data = await api.exchange_code_for_token(
                authorization_code,
                code_verifier,
            )

            # Fetch bikes
            self._bikes = await api.get_bikes()

            if not self._bikes:
                _LOGGER.error("No bikes found for this account")
                errors["base"] = "no_bikes"

            if not errors:
                # Store tokens for next step
                self.context["access_token"] = api.access_token
                self.context["refresh_token"] = api.refresh_token

                # If only one bike, auto-select it
                if len(self._bikes) == 1:
                    bike = self._bikes[0]
                    bike_id = bike["id"]
                    bike_name = _build_bike_name(bike)

                    return self.async_create_entry(
                        title=bike_name,
                        data={
                            CONF_ACCESS_TOKEN: api.access_token,
                            CONF_REFRESH_TOKEN: api.refresh_token,
                            CONF_BIKE_ID: bike_id,
                            CONF_BIKE_NAME: bike_name,
                        },
                    )

                # Multiple bikes - let user choose
                return await self.async_step_select_bike()

        except BoschEBikeAuthError as err:
            _LOGGER.error("Authentication failed: %s", err)
            errors["base"] = "auth_error"
        except BoschEBikeAPIError as err:
            _LOGGER.error("API error: %s", err)
            errors["base"] = "api_error"
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error: %s", err)
            errors["base"] = "unknown"

        # Show form again with errors or regenerate auth URL
        auth_url = BoschEBikeAPI.build_auth_url(self._code_challenge)
        return self.async_show_form(
            step_id="auth",
            description_placeholders={"auth_url": auth_url},
            data_schema=vol.Schema({
                vol.Required(CONF_CODE): str,
            }),
            errors=errors,
        )

    async def async_step_select_bike(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle bike selection when multiple bikes exist."""
        if user_input is not None:
            # Get selected bike
            bike_id = user_input[CONF_BIKE_ID]

            # Find bike details
            bike = next((b for b in self._bikes if b["id"] == bike_id), None)
            if not bike:
                return self.async_abort(reason="bike_not_found")

            bike_name = _build_bike_name(bike)

            return self.async_create_entry(
                title=bike_name,
                data={
                    CONF_ACCESS_TOKEN: self.context["access_token"],
                    CONF_REFRESH_TOKEN: self.context["refresh_token"],
                    CONF_BIKE_ID: bike_id,
                    CONF_BIKE_NAME: bike_name,
                },
            )

        # Build bike selection options
        bike_options = {
            bike["id"]: _build_bike_name(bike)
            for bike in self._bikes
        }

        return self.async_show_form(
            step_id="select_bike",
            data_schema=vol.Schema({
                vol.Required(CONF_BIKE_ID): vol.In(bike_options),
            }),
        )
