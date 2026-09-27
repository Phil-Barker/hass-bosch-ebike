"""Device tracker platform for Bosch eBike integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BoschEBikeDataUpdateCoordinator
from .picture import picture_path

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bosch eBike device tracker from a config entry."""
    coordinator: BoschEBikeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([BoschEBikeDeviceTracker(coordinator)])


class BoschEBikeDeviceTracker(CoordinatorEntity[BoschEBikeDataUpdateCoordinator], TrackerEntity):
    """Last known GPS location of a Bosch eBike (ConnectModule)."""

    _attr_has_entity_name = True
    _attr_name = "Location"
    _attr_translation_key = "location"
    _attr_icon = "mdi:bicycle-electric"

    def __init__(self, coordinator: BoschEBikeDataUpdateCoordinator) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)

        # Set unique ID
        self._attr_unique_id = f"{coordinator.bike_id}_location"

        # Build enhanced device info from component data
        device_info = {
            "identifiers": {(DOMAIN, coordinator.bike_id)},
            "name": coordinator.bike_name,
            "manufacturer": "Bosch",
        }

        # Add component details if available
        if coordinator.data and "components" in coordinator.data:
            components = coordinator.data["components"]

            # Set model from drive unit
            drive_unit = components.get("drive_unit", {})
            if drive_unit.get("product_name"):
                device_info["model"] = drive_unit["product_name"]

            # Add software version
            if drive_unit.get("software_version"):
                device_info["sw_version"] = f"DU: {drive_unit['software_version']}"

            # Add serial number
            if drive_unit.get("serial_number"):
                device_info["serial_number"] = drive_unit["serial_number"]

        if not device_info.get("model"):
            device_info["model"] = "eBike with ConnectModule"

        self._attr_device_info = device_info

    @property
    def _location(self) -> dict[str, Any] | None:
        """Return the location data from the coordinator."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("location")

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        location = self._location
        return location["latitude"] if location else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        location = self._location
        return location["longitude"] if location else None

    @property
    def location_accuracy(self) -> int:
        """Return the GPS accuracy of the device in meters."""
        location = self._location
        if not location or location.get("accuracy_m") is None:
            return 0
        return round(location["accuracy_m"])

    @property
    def entity_picture(self) -> str | None:
        """Return the bike picture from the Bosch bike profile."""
        if self.coordinator.data is None:
            return None
        source_url = self.coordinator.data.get("bike", {}).get("picture_url")
        if not source_url:
            return None
        return picture_path(self.coordinator.bike_id, source_url)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional location details."""
        location = self._location
        if not location:
            return {}
        return {
            "altitude": location.get("altitude_m"),
            "detected_at": location.get("detected_at"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Only available once the API has reported a position
        return (
            self.coordinator.last_update_success
            and self._location is not None
        )
