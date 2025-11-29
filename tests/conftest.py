"""Pytest configuration - mocks Home Assistant modules before imports."""
import sys
from unittest.mock import MagicMock

# Mock Home Assistant modules before any imports
# conftest.py is automatically loaded by pytest before test modules


class MockUpdateFailed(Exception):
    """Mock UpdateFailed exception."""
    pass


class MockDataUpdateCoordinator:
    """Mock DataUpdateCoordinator base class."""

    def __init__(self, *args, **kwargs):
        # Store arguments that might be accessed
        if 'update_interval' in kwargs:
            self.update_interval = kwargs['update_interval']


# Create comprehensive mocks
mock_ha = MagicMock()
mock_ha.core = MagicMock()
mock_ha.core.HomeAssistant = MagicMock()
mock_ha.config_entries = MagicMock()
mock_ha.config_entries.ConfigEntry = MagicMock()
mock_ha.const = MagicMock()
mock_ha.const.Platform = MagicMock()
mock_ha.const.Platform.SENSOR = "sensor"
mock_ha.const.Platform.BINARY_SENSOR = "binary_sensor"
mock_ha.const.CONF_ACCESS_TOKEN = "access_token"
mock_ha.const.CONF_REFRESH_TOKEN = "refresh_token"
mock_ha.helpers = MagicMock()
mock_ha.helpers.update_coordinator = MagicMock()
mock_ha.helpers.update_coordinator.DataUpdateCoordinator = MockDataUpdateCoordinator
mock_ha.helpers.update_coordinator.UpdateFailed = MockUpdateFailed
mock_ha.helpers.aiohttp_client = MagicMock()
mock_ha.helpers.aiohttp_client.async_get_clientsession = MagicMock()

# Inject into sys.modules before any imports
sys.modules['homeassistant'] = mock_ha
sys.modules['homeassistant.core'] = mock_ha.core
sys.modules['homeassistant.config_entries'] = mock_ha.config_entries
sys.modules['homeassistant.const'] = mock_ha.const
sys.modules['homeassistant.helpers'] = mock_ha.helpers
sys.modules['homeassistant.helpers.update_coordinator'] = mock_ha.helpers.update_coordinator
sys.modules['homeassistant.helpers.aiohttp_client'] = mock_ha.helpers.aiohttp_client
