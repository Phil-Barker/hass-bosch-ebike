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
        value_fn=lambda data: data.get("battery", {}).get("is_charging"),
    ),
    BoschEBikeBinarySensorEntityDescription(
        key="charger_connected",
        translation_key="charger_connected",
        name="Charger Connected",
        device_class=BinarySensorDeviceClass.PLUG,
        value_fn=lambda data: data.get("battery", {}).get("is_charger_connected"),
    ),
    BoschEBikeBinarySensorEntityDescription(
        key="battery_light_reserve",
        translation_key="battery_light_reserve",
        name="Battery Light Reserve",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("battery", {}).get("is_light_reserve"),
    ),
    BoschEBikeBinarySensorEntityDescription(
        key="bike_locked",
        translation_key="bike_locked",
        name="Bike Locked",
        device_class=BinarySensorDeviceClass.LOCK,
        value_fn=lambda data: data.get("bike", {}).get("is_locked"),
    ),
    BoschEBikeBinarySensorEntityDescription(
        key="light_on",
        translation_key="light_on",
        name="Light On",
        device_class=BinarySensorDeviceClass.LIGHT,
        value_fn=lambda data: data.get("bike", {}).get("light_on"),
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
        
        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.bike_id)},
            "name": coordinator.bike_name,
            "manufacturer": "Bosch",
            "model": "eBike with ConnectModule",
        }

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        if self.coordinator.data is None:
            return None
        
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.coordinator.data)
        
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.is_on is not None
        )

