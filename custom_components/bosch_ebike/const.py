"""Constants for the Bosch eBike integration."""

DOMAIN = "bosch_ebike"

# API URLs
AUTH_URL = "https://p9.authz.bosch.com/auth/realms/obc/protocol/openid-connect/auth"
TOKEN_URL = "https://p9.authz.bosch.com/auth/realms/obc/protocol/openid-connect/token"
API_BASE_URL = "https://obc-rider-profile.prod.connected-biking.cloud"

# OAuth Configuration
CLIENT_ID = "one-bike-app"
REDIRECT_URI = "onebikeapp-ios://com.bosch.ebike.onebikeapp/oauth2redirect"
SCOPE = "openid offline_access"

# API Endpoints
ENDPOINT_BIKE_PROFILE = "/v1/bike-profile"
ENDPOINT_STATE_OF_CHARGE = "/v1/state-of-charge"
ENDPOINT_PROFILE = "/v1/profile"

# Update intervals
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes (ConnectModule updates every 5 min)
TOKEN_REFRESH_INTERVAL = 5400  # 1.5 hours (tokens expire at 2 hours)

# Entity naming
ATTR_BATTERY_LEVEL = "battery_level"
ATTR_CHARGING = "charging"
ATTR_CHARGER_CONNECTED = "charger_connected"
ATTR_REMAINING_ENERGY = "remaining_energy"
ATTR_REACHABLE_RANGE = "reachable_range"
ATTR_ODOMETER = "odometer"
ATTR_LAST_UPDATE = "last_update"
ATTR_CHARGE_CYCLES = "charge_cycles"

# Assist modes for range sensors
ASSIST_MODES = ["eco", "tour", "sport", "turbo"]

# Config flow
CONF_BIKE_ID = "bike_id"
CONF_BIKE_NAME = "bike_name"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_CODE = "code"

# Options
CONF_DISTANCE_UNIT = "distance_unit"
DISTANCE_UNIT_KM = "km"
DISTANCE_UNIT_MI = "mi"

