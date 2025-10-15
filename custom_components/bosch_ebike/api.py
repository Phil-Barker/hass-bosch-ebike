"""API client for Bosch eBike Flow."""
import logging
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import aiohttp
import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    AUTH_URL,
    TOKEN_URL,
    API_BASE_URL,
    CLIENT_ID,
    REDIRECT_URI,
    SCOPE,
    ENDPOINT_BIKE_PROFILE,
    ENDPOINT_STATE_OF_CHARGE,
)

_LOGGER = logging.getLogger(__name__)


class BoschEBikeAPIError(Exception):
    """Base exception for Bosch eBike API errors."""


class BoschEBikeAuthError(BoschEBikeAPIError):
    """Authentication error."""


class BoschEBikeAPI:
    """API client for Bosch eBike Flow."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._token_expires_at: datetime | None = None

    @staticmethod
    def generate_pkce_pair() -> tuple[str, str]:
        """Generate PKCE code verifier and challenge."""
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')
        
        # Generate code challenge
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge

    @staticmethod
    def build_auth_url(code_challenge: str) -> str:
        """Build the OAuth authorization URL."""
        # Generate random nonce and state for security
        nonce = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "kc_idp_hint": "skid",
            "prompt": "login",
            "nonce": nonce,
            "state": state,
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(
        self,
        authorization_code: str,
        code_verifier: str,
    ) -> dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": authorization_code,
            "code_verifier": code_verifier,
            "redirect_uri": REDIRECT_URI,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        try:
            async with async_timeout.timeout(10):
                async with self._session.post(
                    TOKEN_URL,
                    data=data,
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        _LOGGER.error("Token exchange failed: %s - %s", response.status, error_text)
                        raise BoschEBikeAuthError(f"Token exchange failed ({response.status}): {error_text}")
                    
                    token_data = await response.json()
                    
                    self._access_token = token_data["access_token"]
                    self._refresh_token = token_data["refresh_token"]
                    
                    # Calculate expiration time
                    expires_in = token_data.get("expires_in", 7200)  # Default 2 hours
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    _LOGGER.debug("Successfully exchanged code for tokens")
                    return token_data
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Error exchanging code for token: %s", err)
            raise BoschEBikeAuthError(f"Failed to exchange code: {err}") from err

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh the access token."""
        if not self._refresh_token:
            raise BoschEBikeAuthError("No refresh token available")
        
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": self._refresh_token,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        try:
            async with async_timeout.timeout(10):
                async with self._session.post(
                    TOKEN_URL,
                    data=data,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    token_data = await response.json()
                    
                    self._access_token = token_data["access_token"]
                    self._refresh_token = token_data.get("refresh_token", self._refresh_token)
                    
                    # Calculate expiration time
                    expires_in = token_data.get("expires_in", 7200)
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    _LOGGER.debug("Successfully refreshed access token")
                    return token_data
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Error refreshing token: %s", err)
            raise BoschEBikeAuthError(f"Failed to refresh token: {err}") from err

    async def ensure_valid_token(self) -> None:
        """Ensure we have a valid access token."""
        # Refresh if token expires in less than 10 minutes
        if self._token_expires_at:
            time_until_expiry = self._token_expires_at - datetime.now()
            if time_until_expiry < timedelta(minutes=10):
                _LOGGER.debug("Token expiring soon, refreshing...")
                await self.refresh_access_token()
        elif self._refresh_token:
            # No expiration time set, try to refresh
            await self.refresh_access_token()

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an API request."""
        await self.ensure_valid_token()
        
        if not self._access_token:
            raise BoschEBikeAuthError("No access token available")
        
        headers = kwargs.pop("headers", {})
        headers.update({
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        })
        
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            async with async_timeout.timeout(10):
                async with self._session.request(
                    method,
                    url,
                    headers=headers,
                    **kwargs,
                ) as response:
                    if response.status == 401:
                        # Try to refresh token and retry once
                        _LOGGER.debug("Got 401, attempting token refresh")
                        await self.refresh_access_token()
                        
                        headers["Authorization"] = f"Bearer {self._access_token}"
                        async with self._session.request(
                            method,
                            url,
                            headers=headers,
                            **kwargs,
                        ) as retry_response:
                            retry_response.raise_for_status()
                            return await retry_response.json()
                    
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                _LOGGER.debug("Resource not found (404): %s", endpoint)
                return None
            _LOGGER.error("API request error: %s", err)
            raise BoschEBikeAPIError(f"API request failed: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error: %s", err)
            raise BoschEBikeAPIError(f"Connection failed: {err}") from err

    async def get_bikes(self) -> list[dict[str, Any]]:
        """Get all bikes for the authenticated user."""
        _LOGGER.debug("Fetching bike list")
        response = await self._api_request("GET", ENDPOINT_BIKE_PROFILE)
        
        if not response:
            return []
        
        bikes = response.get("data", [])
        _LOGGER.debug("Found %d bike(s)", len(bikes))
        return bikes

    async def get_bike_profile(self, bike_id: str) -> dict[str, Any] | None:
        """Get detailed bike profile."""
        _LOGGER.debug("Fetching bike profile for %s", bike_id)
        response = await self._api_request(
            "GET",
            f"{ENDPOINT_BIKE_PROFILE}/{bike_id}"
        )
        return response

    async def get_state_of_charge(self, bike_id: str) -> dict[str, Any] | None:
        """Get state of charge data from ConnectModule."""
        _LOGGER.debug("Fetching state of charge for %s", bike_id)
        try:
            response = await self._api_request(
                "GET",
                f"{ENDPOINT_STATE_OF_CHARGE}/{bike_id}"
            )
            return response
        except BoschEBikeAPIError:
            # 404 is expected when bike is offline
            return None

    async def get_battery_data(self, bike_id: str) -> dict[str, Any]:
        """Get comprehensive battery data (tries both endpoints)."""
        # Try state-of-charge first (faster, from ConnectModule)
        soc_data = await self.get_state_of_charge(bike_id)
        
        # Always get bike profile for complete data
        profile_data = await self.get_bike_profile(bike_id)
        
        if not profile_data:
            raise BoschEBikeAPIError(f"Failed to fetch bike profile for {bike_id}")
        
        # Extract battery info from profile
        attributes = profile_data.get("data", {}).get("attributes", {})
        battery = attributes.get("batteries", [{}])[0]
        drive_unit = attributes.get("driveUnit", {})
        
        # Build combined data structure
        data = {
            "bike_id": bike_id,
            "source": "combined",
            "timestamp": datetime.now().isoformat(),
            
            # Battery basics (prefer SoC data if available)
            "battery_level": battery.get("batteryLevel"),
            "remaining_energy": battery.get("remainingEnergy"),
            "total_energy": battery.get("totalEnergy"),
            "is_charging": battery.get("isCharging"),
            "is_charger_connected": battery.get("isChargerConnected"),
            "charge_cycles": battery.get("numberOfFullChargeCycles", {}).get("total"),
            
            # Bike info
            "brand": attributes.get("brandName"),
            "odometer": drive_unit.get("totalDistanceTraveled"),
            "is_locked": drive_unit.get("lock", {}).get("isLocked"),
            
            # From ConnectModule (if available)
            "connect_module_data": None,
        }
        
        # Override/add data from state-of-charge if available
        if soc_data:
            data["connect_module_data"] = soc_data
            data["battery_level"] = soc_data.get("stateOfCharge", data["battery_level"])
            data["is_charging"] = soc_data.get("chargingActive", data["is_charging"])
            data["is_charger_connected"] = soc_data.get("chargerConnected", data["is_charger_connected"])
            data["remaining_energy"] = soc_data.get("remainingEnergyForRider", data["remaining_energy"])
            data["reachable_range"] = soc_data.get("reachableRange", [])
            data["odometer"] = soc_data.get("odometer", data["odometer"])
            data["last_update"] = soc_data.get("stateOfChargeLatestUpdate")
        
        return data

    @property
    def access_token(self) -> str | None:
        """Get the current access token."""
        return self._access_token

    @property
    def refresh_token(self) -> str | None:
        """Get the current refresh token."""
        return self._refresh_token

