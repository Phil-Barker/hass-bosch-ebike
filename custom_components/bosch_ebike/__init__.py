"""The Bosch eBike integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BoschEBikeAPI
from .const import DOMAIN, CONF_BIKE_ID, CONF_BIKE_NAME, CONF_REFRESH_TOKEN
from .coordinator import BoschEBikeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Platforms to set up
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bosch eBike from a config entry."""
    _LOGGER.debug("Setting up Bosch eBike integration")
    
    # Get tokens from config entry
    access_token = entry.data[CONF_ACCESS_TOKEN]
    refresh_token = entry.data.get(CONF_REFRESH_TOKEN)
    bike_id = entry.data[CONF_BIKE_ID]
    bike_name = entry.data.get(CONF_BIKE_NAME, "eBike")
    
    # Create API client
    session = async_get_clientsession(hass)
    api = BoschEBikeAPI(
        session=session,
        access_token=access_token,
        refresh_token=refresh_token,
    )
    
    # Create update coordinator
    coordinator = BoschEBikeDataUpdateCoordinator(
        hass=hass,
        api=api,
        bike_id=bike_id,
        bike_name=bike_name,
    )
    
    _LOGGER.info(
        "Created coordinator for %s with update interval: %s",
        bike_name,
        coordinator.update_interval,
    )
    
    # Fetch initial data
    _LOGGER.info("Performing initial data refresh for %s", bike_name)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.info("Initial data refresh complete for %s", bike_name)
    
    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "bike_id": bike_id,
        "bike_name": bike_name,
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register options update listener
    entry.add_update_listener(async_update_options)
    
    _LOGGER.info(
        "Bosch eBike integration setup complete for %s (ID: %s)",
        bike_name,
        bike_id,
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Bosch eBike integration")
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Remove data
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

