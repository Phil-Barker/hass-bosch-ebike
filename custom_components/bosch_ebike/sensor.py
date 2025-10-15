"""Sensor platform for Bosch eBike integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BoschEBikeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class BoschEBikeSensorEntityDescription(SensorEntityDescription):
    """Describes Bosch eBike sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None


SENSORS: tuple[BoschEBikeSensorEntityDescription, ...] = (
    BoschEBikeSensorEntityDescription(
        key="battery_level",
        translation_key="battery_level",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("level_percent"),
    ),
    BoschEBikeSensorEntityDescription(
        key="battery_remaining_energy",
        translation_key="battery_remaining_energy",
        name="Battery Remaining Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("remaining_wh"),
    ),
    BoschEBikeSensorEntityDescription(
        key="battery_capacity",
        translation_key="battery_capacity",
        name="Battery Capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("total_capacity_wh"),
    ),
    BoschEBikeSensorEntityDescription(
        key="battery_reachable_range",
        translation_key="battery_reachable_range",
        name="Reachable Range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery", {}).get("reachable_range_km"),
        entity_registry_enabled_default=False,  # Only available when bike is online
    ),
    BoschEBikeSensorEntityDescription(
        key="total_distance",
        translation_key="total_distance",
        name="Total Distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: (
            round(data.get("bike", {}).get("total_distance_m", 0) / 1000, 2)
            if data.get("bike", {}).get("total_distance_m") is not None
            else None
        ),
    ),
    BoschEBikeSensorEntityDescription(
        key="charge_cycles",
        translation_key="charge_cycles",
        name="Charge Cycles",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("battery", {}).get("charge_cycles_total"),
    ),
    BoschEBikeSensorEntityDescription(
        key="lifetime_energy_delivered",
        translation_key="lifetime_energy_delivered",
        name="Lifetime Energy Delivered",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: (
            round(data.get("battery", {}).get("delivered_lifetime_wh", 0) / 1000, 2)
            if data.get("battery", {}).get("delivered_lifetime_wh") is not None
            else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bosch eBike sensors from a config entry."""
    coordinator: BoschEBikeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = [
        BoschEBikeSensor(coordinator, description)
        for description in SENSORS
    ]
    
    async_add_entities(entities)


class BoschEBikeSensor(CoordinatorEntity[BoschEBikeDataUpdateCoordinator], SensorEntity):
    """Representation of a Bosch eBike sensor."""

    entity_description: BoschEBikeSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BoschEBikeDataUpdateCoordinator,
        description: BoschEBikeSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
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
            and self.native_value is not None
        )

