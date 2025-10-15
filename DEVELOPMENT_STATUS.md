# Bosch eBike - Home Assistant Integration Development Status

## ✅ Phase 1: Setup & Authentication - COMPLETE

### What We Built

#### 1. Integration Structure

- ✅ `manifest.json` - Integration metadata
- ✅ `const.py` - All constants (URLs, endpoints, intervals)
- ✅ `api.py` - Complete API client with OAuth 2.0 + PKCE
- ✅ `config_flow.py` - OAuth configuration flow
- ✅ `__init__.py` - Integration setup and platform loading
- ✅ `strings.json` - UI translations
- ✅ `translations/en.json` - English translations

#### 2. Features Implemented

**API Client (`api.py`):**

- ✅ PKCE generation (code verifier & challenge)
- ✅ OAuth authorization URL building
- ✅ Code-to-token exchange
- ✅ Automatic token refresh (before expiration)
- ✅ Get all bikes for user
- ✅ Get bike profile (detailed info)
- ✅ Get state of charge (ConnectModule data)
- ✅ Combined battery data (tries both endpoints)
- ✅ Error handling (401 retry, 404 handling, etc.)

**Config Flow (`config_flow.py`):**

- ✅ OAuth 2.0 with PKCE authentication
- ✅ External authentication step (browser redirect)
- ✅ Automatic bike discovery
- ✅ Single bike auto-selection
- ✅ Multiple bike selection UI
- ✅ Token storage in config entry
- ✅ Options flow foundation

**Integration Setup (`__init__.py`):**

- ✅ Entry setup with API client initialization
- ✅ Platform forwarding (sensor, binary_sensor)
- ✅ Unload and reload support
- ✅ Data storage in hass.data

### File Structure

```text
custom_components/bosch_ebike/
├── __init__.py              ✅ Integration setup
├── api.py                   ✅ API client
├── config_flow.py           ✅ OAuth flow
├── const.py                 ✅ Constants
├── manifest.json            ✅ Metadata
├── strings.json             ✅ UI strings
└── translations/
    └── en.json              ✅ English translation
```

---

## 📋 Next Steps

### Phase 2: Data Coordinator (Next Up!)

Create the data update coordinator that polls the API every 5 minutes.

**To Build:**

- [ ] `coordinator.py` - DataUpdateCoordinator subclass
  - [ ] Fetch battery data every 5 minutes
  - [ ] Handle token refresh automatically
  - [ ] Error handling with exponential backoff
  - [ ] Update all sensors when data arrives

**Files to Create:**

```python
# coordinator.py
class BoschEBikeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""
    
    def __init__(self, hass, api, bike_id):
        super().__init__(
            hass,
            _LOGGER,
            name="Bosch eBike",
            update_interval=timedelta(minutes=5),
        )
        self.api = api
        self.bike_id = bike_id
    
    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.api.get_battery_data(self.bike_id)
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")
```

### Phase 3: Sensor Entities

Create all the sensor entities.

**To Build:**

- [ ] `sensor.py` - All sensors
  - [ ] Battery level sensor (%)
  - [ ] Remaining energy sensor (Wh)
  - [ ] Range sensors (4x - eco, tour, sport, turbo)
  - [ ] Odometer sensor (km)
  - [ ] Charge cycles sensor

### Phase 4: Binary Sensor Entities

Create binary sensors for on/off states.

**To Build:**

- [ ] `binary_sensor.py` - Binary sensors
  - [ ] Charging status (on/off)
  - [ ] Charger connected (on/off)
  - [ ] Bike lock status (locked/unlocked)

### Phase 5: Testing & Polish

- [ ] Test with single bike
- [ ] Test with multiple bikes
- [ ] Test token refresh flow
- [ ] Test offline bike handling
- [ ] Add diagnostics
- [ ] Update documentation
- [ ] Create example automations

---

## 🧪 Testing Phase 1

### How to Test

1. **Copy integration to Home Assistant:**

   ```bash
   cp -r custom_components/bosch_ebike ~/.homeassistant/custom_components/
   ```

2. **Restart Home Assistant**

3. **Add Integration:**
   - Settings → Devices & Services
   - Add Integration → Search "Bosch eBike"
   - Follow OAuth flow in browser
   - Select your bike (if multiple)

4. **Verify:**
   - Integration appears in Devices & Services
   - No errors in logs
   - Wait for Phase 2 to see actual sensor data!

### Expected Behavior

- ✅ Integration shows up in Add Integration dialog
- ✅ OAuth redirect opens in browser
- ✅ Successfully authenticates with Bosch
- ✅ Discovers bikes automatically
- ✅ Creates config entry with bike info
- ❌ No sensors yet (Phase 3)
- ❌ No data updates yet (Phase 2)

---

## 📊 Progress Overview

| Phase | Status | Files | Features |
|-------|--------|-------|----------|
| 1. Setup & Auth | ✅ **DONE** | 7 files | OAuth, API client, Config flow |
| 2. Coordinator | 📝 Next | 1 file | Data polling |
| 3. Sensors | ⏳ Pending | 1 file | 6 sensors |
| 4. Binary Sensors | ⏳ Pending | 1 file | 3 binary sensors |
| 5. Testing & Polish | ⏳ Pending | Multiple | Testing, docs |

---

## 🎯 What You Can Do Now

1. **Test Phase 1** - Try adding the integration in HA
2. **Review the code** - Check if anything needs adjustment
3. **Take a break!** - Phase 1 is substantial work
4. **When ready:** Let's build Phase 2 (coordinator)

---

## 📝 Notes

### OAuth Flow

The config flow handles the complex OAuth 2.0 + PKCE flow:

1. Generates PKCE parameters
2. Redirects user to Bosch auth
3. Captures authorization code
4. Exchanges for tokens
5. Discovers bikes
6. Creates config entry

### Token Management

Tokens are automatically refreshed:

- Access token expires after 2 hours
- Refresh happens automatically before expiration
- No user interaction needed
- Handles 401 errors gracefully

### Multi-Bike Support

Already built in:

- Discovers all bikes on account
- Lets user choose if multiple
- Each bike gets its own config entry
- Can add multiple bikes as separate integrations

---

## 🐛 Known Issues / TODO

- [ ] Need to handle "onebikeconnect://" redirect in HA
  - This may require custom redirect handler
  - Or use localhost callback URL
- [ ] Test with actual HA instance
- [ ] Verify PKCE flow works end-to-end
- [ ] Add better error messages
- [ ] Consider rate limiting handling

---

## 📚 Reference

- **Main Guide:** `docs/HOME_ASSISTANT_INTEGRATION_GUIDE.md`
- **API Reference:** `docs/QUICK_REFERENCE.md`
- **Working Example:** `monitor_battery.py`
- **Project README:** `README.md`

---

**Ready to continue?** Let's build Phase 2: Data Coordinator! 🚀
