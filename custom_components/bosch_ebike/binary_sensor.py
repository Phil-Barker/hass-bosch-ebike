"""Binary sensor platform for Bosch eBike integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BoschEBikeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class BoschEBikeBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Bosch eBike binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None] | None = None


BINARY_SENSORS: tuple[BoschEBikeBinarySensorEntityDescription, ...] = (
    BoschEBikeBinarySensorEntityDescription(
        key="battery_charging",
        translation_key="battery_charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: bool(data.get("battery", {}).get("is_charging")),
    ),
    # Note: charger_connected is unreliable - ConnectModule stops updating when
    # bike is unplugged and powered off, so we never get the "unplugged" event
    BoschEBikeBinarySensorEntityDescription(
        key="charger_connected",
        translation_key="charger_connected",
        name="Charger Connected",
        device_class=BinarySensorDeviceClass.PLUG,
        value_fn=lambda data: bool(data.get("battery", {}).get("is_charger_connected")),
        entity_registry_enabled_default=False,  # Disabled - unreliable due to ConnectModule behavior
    ),
    # Lock and alarm sensors are unreliable - need further API exploration
    BoschEBikeBinarySensorEntityDescription(
        key="lock_enabled",
        translation_key="lock_enabled",
        name="Lock Enabled",
        device_class=BinarySensorDeviceClass.LOCK,
        value_fn=lambda data: (
            data.get("bike", {}).get("is_locked") 
            if data.get("bike", {}).get("is_locked") is not None
            else data.get("bike", {}).get("lock_enabled")
        ),
        entity_registry_enabled_default=False,  # Disabled - unreliable, needs investigation
    ),
    BoschEBikeBinarySensorEntityDescription(
        key="alarm_enabled",
        translation_key="alarm_enabled",
        name="Alarm Enabled",
        # No device_class - just show On/Off
        value_fn=lambda data: data.get("bike", {}).get("alarm_enabled"),
        entity_registry_enabled_default=False,  # Disabled - unreliable, needs investigation
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bosch eBike binary sensors from a config entry."""
    coordinator: BoschEBikeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = [
        BoschEBikeBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    ]
    
    async_add_entities(entities)


class BoschEBikeBinarySensor(CoordinatorEntity[BoschEBikeDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a Bosch eBike binary sensor."""

    entity_description: BoschEBikeBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BoschEBikeDataUpdateCoordinator,
        description: BoschEBikeBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        
        # Set unique ID
        self._attr_unique_id = f"{coordinator.bike_id}_{description.key}"
        
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
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        if self.coordinator.data is None:
            return None
        
        if self.entity_description.value_fn is not None:
            value = self.entity_description.value_fn(self.coordinator.data)
            
            # Log state changes for critical sensors
            if self.entity_description.key in ("charger_connected", "battery_charging"):
                if not hasattr(self, "_last_logged_state") or self._last_logged_state != value:
                    _LOGGER.info(
                        "Binary sensor %s state: %s (previous: %s)",
                        self.entity_description.key,
                        value,
                        getattr(self, "_last_logged_state", "unknown"),
                    )
                    self._last_logged_state = value
            
            return value
        
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is available if coordinator succeeded
        # Even if individual values are None, we want to show the entity
        # (it will just show as Off/Unknown)
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
        )

