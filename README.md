# Bosch eBike Flow - Home Assistant Integration

Home Assistant integration for Bosch eBike with ConnectModule support. Monitor battery status, charging state, and enable smart charging automations.

## 🎯 Features

- **Battery Monitoring**: Real-time battery level, remaining energy, and charge cycles
- **Charging Status**: Know when bike is charging and charger is connected
- **Range Estimates**: See range for each assist mode (Eco, Tour, Sport, Turbo)
- **Smart Charging**: Stop charging at optimal level (e.g., 80%) for battery health
- **Multiple Bikes**: Support for multiple eBikes on one account
- **Auto Updates**: Data refreshes every 5 minutes via ConnectModule

## 📁 Project Structure

```
├── custom_components/bosch_ebike/  # Home Assistant integration (in development)
├── docs/                           # Complete documentation
│   ├── HOME_ASSISTANT_INTEGRATION_GUIDE.md  # Main technical guide
│   ├── QUICK_REFERENCE.md                   # Code snippets & cheat sheet
│   └── ...more docs...
├── exploration/                    # API discovery scripts and test data
├── monitor_battery.py              # Standalone battery monitor script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- Bosch eBike with ConnectModule (BCM3100 or similar)
- Flow+ subscription (~40 EUR/year) for live battery data
- Bosch Flow account
- Home Assistant 2023.1+

### Test the API

Before installing the integration, test that your bike is accessible:

```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate (will open browser)
# Follow the authentication flow to get tokens

# Monitor battery status
python3 monitor_battery.py

# Continuous monitoring (updates every 60 seconds)
python3 monitor_battery.py monitor
```

### Install Integration

#### Development/Testing Deployment

Use the deployment script to sync to your Home Assistant instance via SSH:

```bash
# Quick deploy (if using homeassistant.local)
./deploy-dev.sh

# Or specify your HA IP
HA_HOST=192.168.1.100 ./deploy-dev.sh

# Or create .env file with your config
cp .env.example .env
# Edit .env with your details  
source .env && ./deploy-dev.sh
```

**📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.**

After deployment:
- Settings → Devices & Services → Add Integration → "Bosch eBike"

#### End User Installation (Future)

Once published, users can install via:
- **HACS** (Home Assistant Community Store) - recommended
- **Manual:** Copy `custom_components/bosch_ebike` to config directory

## 📊 Example Automation

Stop charging at 80% for optimal battery health:

```yaml
automation:
  - alias: "Stop eBike Charging at 80%"
    trigger:
      platform: numeric_state
      entity_id: sensor.my_ebike_battery
      above: 80
    condition:
      condition: state
      entity_id: binary_sensor.my_ebike_charging
      state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.ebike_charger_plug
      - service: notify.mobile_app
        data:
          title: "eBike Charged"
          message: "Battery at {{ states('sensor.my_ebike_battery') }}% - optimal charge reached"
```

## 📚 Documentation

### For Developers

- **[HOME_ASSISTANT_INTEGRATION_GUIDE.md](docs/HOME_ASSISTANT_INTEGRATION_GUIDE.md)** - Complete technical reference
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - API endpoints and code snippets
- **[FINAL_ANSWER.md](docs/FINAL_ANSWER.md)** - Discovery summary and authentication guide

### For Users

- **[HOW_TO_ENABLE_LIVE_SOC.md](docs/HOW_TO_ENABLE_LIVE_SOC.md)** - Enable live battery data in Flow app
- **[BATTERY_STATUS_SOLUTION.md](docs/BATTERY_STATUS_SOLUTION.md)** - Understanding battery data

## 🔧 Development Status

- [x] API Discovery & Documentation
- [x] Authentication (OAuth 2.0 with PKCE)
- [x] Battery Data Polling
- [x] Working Test Scripts
- [ ] **Phase 1: HA Integration Setup** ← IN PROGRESS
- [ ] Phase 2: Config Flow
- [ ] Phase 3: Data Coordinator
- [ ] Phase 4: Entities (Sensors & Binary Sensors)
- [ ] Phase 5: Release & Testing

## 🛠️ API Endpoints

```python
# Authentication
POST https://p9.authz.bosch.com/auth/realms/obc/protocol/openid-connect/token

# Get all bikes
GET https://obc-rider-profile.prod.connected-biking.cloud/v1/bike-profile

# Get battery status (requires Flow+)
GET https://obc-rider-profile.prod.connected-biking.cloud/v1/state-of-charge/{bike_id}
```

## 📈 Entities Created

### Sensors
- `sensor.{bike}_battery` - Battery level (%)
- `sensor.{bike}_remaining_energy` - Remaining energy (Wh)
- `sensor.{bike}_range_eco` - Range in Eco mode (km)
- `sensor.{bike}_range_tour` - Range in Tour mode (km)
- `sensor.{bike}_range_sport` - Range in Sport mode (km)
- `sensor.{bike}_range_turbo` - Range in Turbo mode (km)
- `sensor.{bike}_odometer` - Total distance (km)
- `sensor.{bike}_charge_cycles` - Charge cycle count

### Binary Sensors
- `binary_sensor.{bike}_charging` - Is currently charging
- `binary_sensor.{bike}_charger_connected` - Is charger plugged in
- `binary_sensor.{bike}_lock` - Lock status (if supported)

## 🤝 Contributing

This integration is in active development. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Bosch for the Flow API
- ioBroker Bosch eBike adapter community for inspiration
- Home Assistant community

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: See `docs/` folder
- **Testing**: Use `monitor_battery.py` script

---

**Current Phase**: Building Home Assistant integration (Phase 1) 🚧
