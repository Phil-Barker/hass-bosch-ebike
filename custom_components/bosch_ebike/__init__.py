"""The Bosch eBike integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BoschEBikeAPI
from .const import DOMAIN, CONF_BIKE_ID, CONF_BIKE_NAME

_LOGGER = logging.getLogger(__name__)

# Platforms to set up (Phase 2 - will be enabled when sensors are created)
# PLATFORMS: list[Platform] = [
#     Platform.SENSOR,
#     Platform.BINARY_SENSOR,
# ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bosch eBike from a config entry."""
    _LOGGER.debug("Setting up Bosch eBike integration")
    
    # Get tokens from config entry
    access_token = entry.data[CONF_ACCESS_TOKEN]
    refresh_token = entry.data.get("refresh_token")
    bike_id = entry.data[CONF_BIKE_ID]
    bike_name = entry.data.get(CONF_BIKE_NAME, "eBike")
    
    # Create API client
    session = async_get_clientsession(hass)
    api = BoschEBikeAPI(
        session=session,
        access_token=access_token,
        refresh_token=refresh_token,
    )
    
    # Store API client and bike info in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "bike_id": bike_id,
        "bike_name": bike_name,
    }
    
    # Set up platforms (Phase 2 - will be enabled when sensors are created)
    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info(
        "Bosch eBike integration setup complete for %s (ID: %s)",
        bike_name,
        bike_id,
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Bosch eBike integration")
    
    # Unload platforms (Phase 2 - will be enabled when sensors are created)
    # unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Remove data
    hass.data[DOMAIN].pop(entry.entry_id)
    
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

