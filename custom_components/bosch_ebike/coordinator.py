"""DataUpdateCoordinator for Bosch eBike integration."""
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BoschEBikeAPI, BoschEBikeAPIError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Poll every 5 minutes (300 seconds)
UPDATE_INTERVAL = timedelta(minutes=5)


class BoschEBikeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Bosch eBike data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: BoschEBikeAPI,
        bike_id: str,
        bike_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{bike_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self.bike_id = bike_id
        self.bike_name = bike_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Bosch eBike API."""
        try:
            _LOGGER.debug("Fetching data for bike %s", self.bike_id)
            
            # Fetch bike profile (static info + last known battery state)
            profile_data = await self.api.get_bike_profile(self.bike_id)
            
            # Try to fetch live state of charge (only works when bike is online/charging)
            soc_data = None
            try:
                soc_data = await self.api.get_state_of_charge(self.bike_id)
                _LOGGER.debug("Got live state-of-charge data")
            except BoschEBikeAPIError as err:
                # This is expected when bike is offline - not an error
                _LOGGER.debug("Live state-of-charge not available (bike offline?): %s", err)
            
            # Combine the data
            combined_data = self._combine_bike_data(profile_data, soc_data)
            
            _LOGGER.debug("Successfully fetched bike data: battery=%s%%", 
                         combined_data.get("battery", {}).get("level_percent"))
            
            return combined_data
            
        except BoschEBikeAPIError as err:
            _LOGGER.error("Error fetching bike data: %s", err)
            raise UpdateFailed(f"Error communicating with Bosch API: {err}") from err

    def _combine_bike_data(
        self,
        profile_data: dict[str, Any],
        soc_data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Combine bike profile and state-of-charge data."""
        try:
            # Extract from profile
            bike_attrs = profile_data.get("data", {}).get("attributes", {})
            battery = bike_attrs.get("batteries", [{}])[0]
            drive_unit = bike_attrs.get("driveUnit", {})
            
            # Start with profile data
            combined = {
                "battery": {
                    "level_percent": battery.get("batteryLevel"),
                    "remaining_wh": battery.get("remainingEnergy"),
                    "total_capacity_wh": battery.get("totalEnergy"),
                    "is_charging": battery.get("isCharging"),
                    "is_charger_connected": battery.get("isChargerConnected"),
                    "is_light_reserve": battery.get("isLightReserveReached"),
                    "charge_cycles_total": battery.get("numberOfFullChargeCycles", {}).get("total"),
                    "delivered_lifetime_wh": battery.get("deliveredWhOverLifetime"),
                },
                "bike": {
                    "total_distance_m": drive_unit.get("totalDistanceTraveled"),
                    "is_locked": drive_unit.get("lock", {}).get("isLocked"),
                    "light_on": drive_unit.get("bikeLight", {}).get("isSwitchedOn"),
                },
                "last_update": None,
                "live_data_available": False,
            }
            
            # If we have live state-of-charge data, use it to fill in/override nulls
            if soc_data:
                combined["live_data_available"] = True
                combined["last_update"] = soc_data.get("stateOfChargeLatestUpdate")
                
                # Use live data to fill in null values from profile
                if combined["battery"]["level_percent"] is None:
                    combined["battery"]["level_percent"] = soc_data.get("stateOfCharge")
                
                if combined["battery"]["is_charging"] is None:
                    combined["battery"]["is_charging"] = soc_data.get("chargingActive")
                
                if combined["battery"]["is_charger_connected"] is None:
                    combined["battery"]["is_charger_connected"] = soc_data.get("chargerConnected")
                
                # Add live-only data
                combined["battery"]["reachable_range_km"] = soc_data.get("reachableRange")
                combined["battery"]["remaining_energy_rider_wh"] = soc_data.get("remainingEnergyForRider")
                
                # Update odometer from live data if available
                if soc_data.get("odometer") is not None:
                    combined["bike"]["total_distance_m"] = soc_data.get("odometer")
            
            return combined
            
        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.error("Error combining bike data: %s", err)
            raise UpdateFailed(f"Error parsing bike data: {err}") from err

