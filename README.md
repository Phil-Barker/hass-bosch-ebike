# Bosch eBike Flow - Home Assistant Integration

Home Assistant integration for Bosch eBike with ConnectModule support. Monitor battery status, charging state, and enable smart charging automations.

## 🎯 Features

- **Battery Monitoring**: Real-time battery level, remaining energy, capacity, and charge cycles
- **Charging Status**: Know when bike is charging and charger is connected
- **Distance Tracking**: Total distance traveled with lifetime energy delivered
- **Lock & Alarm Status**: Monitor bike lock and alarm feature status
- **Smart Charging**: Create automations to stop charging at optimal level (e.g., 80%)
- **Multiple Bikes**: Support for multiple eBikes on one account
- **Auto Updates**: Data refreshes every 5 minutes via ConnectModule
- **Component Info**: View software versions and serial numbers for all bike components

## 📁 Project Structure

```text
├── custom_components/bosch_ebike/  # Home Assistant integration
│   ├── __init__.py                 # Integration setup & coordinator
│   ├── manifest.json               # Integration metadata
│   ├── config_flow.py              # OAuth setup flow
│   ├── coordinator.py              # Data update coordinator
│   ├── sensor.py                   # Sensor entities
│   ├── binary_sensor.py            # Binary sensor entities
│   ├── api.py                      # Bosch API client
│   ├── const.py                    # Constants
│   └── strings.json                # UI strings
├── deploy-dev.sh                   # Development deployment script
├── .env.example                    # Configuration template
├── DEPLOYMENT.md                   # Developer deployment guide
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- Bosch eBike with ConnectModule (BCM3100 or similar)
- Flow+ subscription (~40 EUR/year) for live battery data
- Bosch Flow account
- Home Assistant 2023.1+

### Installation

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

1. Restart Home Assistant
2. Go to: Settings → Devices & Services → Add Integration
3. Search for "Bosch eBike"
4. Follow the OAuth authentication flow

#### Manual Installation

For end users without SSH access:

1. Copy the `custom_components/bosch_ebike` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services

#### HACS Installation (Coming Soon)

We're working on getting this integration added to HACS for easier installation!

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

## ✅ What's Included

This integration provides complete monitoring for your Bosch eBike:

- ✅ **OAuth 2.0 Authentication** - Secure login with your Bosch Flow account
- ✅ **Battery Monitoring** - Level, capacity, remaining energy, charge cycles
- ✅ **Charging Control** - Track charging status for smart automation
- ✅ **Distance Tracking** - Odometer and lifetime energy statistics
- ✅ **Security Features** - Lock and alarm status monitoring
- ✅ **Auto Updates** - Data refreshes every 5 minutes via ConnectModule
- ✅ **Multi-Bike Support** - Manage multiple eBikes from one account
- ✅ **Component Details** - View software versions and serial numbers

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

- **Battery Level** - Battery percentage (%)
- **Battery Remaining Energy** - Remaining energy (Wh)
- **Battery Capacity** - Total battery capacity (Wh)
- **Reachable Range** - Estimated range (km) - *disabled by default, only available when bike is online*
- **Total Distance** - Odometer reading (km)
- **Charge Cycles** - Number of charge cycles
- **Lifetime Energy Delivered** - Total energy delivered over bike lifetime (kWh)

### Binary Sensors

- **Battery Charging** - Is currently charging
- **Charger Connected** - Is charger plugged in
- **Lock Enabled** - Lock feature status
- **Alarm Enabled** - Alarm feature status

### Diagnostic Entities *(disabled by default)*

- **Drive Unit Software** - Drive unit software version
- **Battery Software** - Battery software version
- **ConnectModule Software** - ConnectModule software version
- **Remote Control Software** - Remote control software version

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test with your own eBike setup
5. Submit a pull request

See [DEPLOYMENT.md](DEPLOYMENT.md) for development setup instructions.

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Bosch for the Flow API
- ioBroker Bosch eBike adapter community for inspiration
- Home Assistant community

## ☕ Support This Project

If this integration helps you optimize your eBike charging and you'd like to support continued development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/philbarker)

Your support helps maintain the project and keeps the coffee flowing! ☕

## 📞 Support & Help

- **Issues**: [GitHub Issues](https://github.com/Phil-Barker/hass-bosch-ebike/issues)
- **Questions**: Feel free to open a discussion or issue
- **Contributing**: Pull requests welcome!

---

**Status**: ✅ Integration Complete - Phases 1 & 2 Done!  
Now available for real-world use! 🚲⚡
