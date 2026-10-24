# Bosch eBike Flow Integration for Home Assistant

Monitor your Bosch eBike directly in Home Assistant! Track battery level, charging status, range, and more.

## ⚠️ IMPORTANT: Before You Install

**This integration requires additional hardware and a subscription:**

- 🔌 **ConnectModule hardware** (~€100-150) - sold separately, NOT included with most bikes
- 💳 **Flow+ subscription** (~€30-50/year) - required for cloud connectivity
- 📱 **Bosch eBike Flow app** (Gen 4 / Gen 5 smart system)

**This will NOT work with:**

- ❌ Bosch eBike Connect app (Gen 3 and below)  
- ❌ Bikes without ConnectModule hardware
- ❌ Non-Bosch eBike systems

## Features

### 📊 Sensors (Enabled by Default)

- **Battery Level** - Current battery percentage
- **Battery Remaining Energy** - Energy remaining in Wh
- **Battery Capacity** - Total battery capacity in Wh
- **Battery Charging** - Whether the battery is actively charging
- **Total Distance** - Odometer reading
- **Charge Cycles** - Number of full charge cycles
- **Lifetime Energy Delivered** - Total kWh delivered over the bike's lifetime
- **Location** - Device tracker with the last GPS position reported by the ConnectModule, for zones and the map card

### 🔋 Additional Sensors (Disabled by Default)

- **Reachable Range** - Estimated range in the most economical riding mode (only available when bike is online/charging)
- **Charger Connected** - Whether charger is plugged in (limited reliability - see docs)
- **Lock Status** - Lock enabled status (experimental)
- **Alarm Status** - Alarm enabled status (experimental)

## Perfect For

- 🔌 **Charge Monitoring** - Track your bike's charging progress
- ⚡ **Smart Charging** - Create automations to stop charging at 80% for battery health
- 📱 **Notifications** - Get alerts when charging is complete
- 📊 **Statistics** - Monitor battery health and usage over time
- 🏠 **Smart Home Integration** - Integrate with your existing automations

## Detailed Requirements

### Hardware (Must Purchase Separately)

- **Bosch ConnectModule** - ~€100-150
  - NOT included with most bikes
  - Must be installed on your bike
  - Available from Bosch dealers

### Subscription (Annual Cost)

- **Bosch eBike Flow+** - ~€30-50/year
  - Required for cloud features
  - Subscribe in the Flow app

### Software

- **Bosch eBike Flow app** (Gen 4 / Gen 5 smart system, e.g. Performance Line CX, SX, PX and Cargo Line)
- **Home Assistant** 2024.1.0 or newer

## Installation

1. Add this repository to HACS as a custom repository
2. Search for "Bosch eBike Flow" in HACS
3. Install the integration
4. Restart Home Assistant
5. Go to Settings → Devices & Services → Add Integration
6. Search for "Bosch eBike Flow"
7. Follow the OAuth login flow

## How It Works

The integration polls the Bosch eBike Cloud API every 5 minutes. The ConnectModule on your bike updates the cloud when:

- The bike is charging (plugged in)
- The bike is powered on
- The alarm is triggered by motion

This means sensors update in real-time while charging, making it perfect for monitoring charge sessions and creating smart charging automations.

## Support

- 📖 [Full Documentation](https://github.com/Phil-Barker/hass-bosch-ebike)
- 🐛 [Report Issues](https://github.com/Phil-Barker/hass-bosch-ebike/issues)
- 💬 [Discussions](https://github.com/Phil-Barker/hass-bosch-ebike/discussions)

## Example Automations

### Stop Charging at 80%

```yaml
automation:
  - alias: "Stop eBike charging at 80%"
    trigger:
      - platform: numeric_state
        entity_id: sensor.your_bike_battery_level
        above: 80
    condition:
      - condition: state
        entity_id: binary_sensor.your_bike_battery_charging
        state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.your_smart_plug
```

### Notify When Fully Charged

```yaml
automation:
  - alias: "Notify when eBike fully charged"
    trigger:
      - platform: numeric_state
        entity_id: sensor.your_bike_battery_level
        above: 99
    condition:
      - condition: state
        entity_id: binary_sensor.your_bike_battery_charging
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🚴‍♂️ eBike Ready!"
          message: "Your bike is fully charged and ready to ride!"
```

---

**Note:** This is an unofficial integration and is not affiliated with or endorsed by Bosch eBike Systems.
