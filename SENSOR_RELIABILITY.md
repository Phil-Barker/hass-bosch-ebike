# Bosch eBike Sensor Reliability Analysis

## ConnectModule Update Behavior

The Bosch ConnectModule only updates the API in specific scenarios:

1. **When bike is charging** (plugged in)
2. **When bike is powered on**
3. **When alarm is triggered** (motion detection)

When the bike is unplugged AND powered off AND alarm is inactive, the ConnectModule stops sending updates to the API.

## Sensor Reliability

### ✅ Reliable Sensors (Enabled by Default)

These sensors work well for the primary use case (monitoring charging):

- **Battery Level** - Updates while charging, perfect for "charge to X%" automations
- **Battery Remaining Energy** - Watt-hours remaining
- **Battery Capacity** - Total battery capacity
- **Total Distance** - Odometer reading
- **Charge Cycles** - Number of full charge cycles
- **Lifetime Energy Delivered** - Total kWh delivered over bike's lifetime
- **Battery Charging** - Whether bike is actively charging (reliable during charging sessions)

### ⚠️ Partially Reliable (Enabled but with caveats)

- **Reachable Range** - Array of range estimates for each riding mode (eco/trail/turbo/etc)
  - Only available when bike is online/charging
  - Disabled by default until user enables it
  - Shows first (most economical) mode value

### ❌ Unreliable Sensors (Disabled by Default)

These sensors are disabled because they don't provide accurate state change events:

1. **Charger Connected**
   - **Issue:** When you unplug the charger, the ConnectModule stops updating (because bike is off), so the API never receives the "unplugged" event
   - **What works:** Shows "plugged in" correctly when charging
   - **What doesn't work:** Won't show "unplugged" until bike is next powered on
   - **Automation impact:** Can't trigger on "charger unplugged" events reliably

2. **Lock Enabled**
   - **Issue:** Unclear which API field represents lock state accurately
   - **Data available:** `isLocked` (current state?) and `isEnabled` (feature enabled?)
   - **Current behavior:** Shows as "unlocked" even when bike is physically locked
   - **Status:** Needs further API exploration

3. **Alarm Enabled**
   - **Issue:** Unclear if this updates reliably
   - **Status:** Needs further API exploration

## Primary Use Case

This integration is designed for users who:

- Store their eBike in a garage/shed
- Charge overnight
- Want automations like:
  - ✅ "Notify when battery reaches 80%"
  - ✅ "Turn off smart plug when battery full"
  - ✅ "Alert if charging and battery isn't increasing"
  - ✅ "Charge to specific range (e.g., 20 miles)"
  - ❌ "Alert when charger is unplugged" (unreliable - see above)

## Polling Interval

**Current:** 5 minutes (300 seconds)

**Rationale:**

- While charging, ConnectModule updates frequently
- 5 minute polling provides good balance between responsiveness and API load
- For "charge to X%" automations, 5 minutes is acceptable granularity
- Could be reduced to 2-3 minutes if faster response needed

**Future:** Make configurable (1, 2, 3, 5, 10, 15 minute options)

## Future API Exploration

Based on JWT token audiences, we may have access to:

- `anti-theft-lock` - Potential for lock control
- `anti-theft-theft-detection` - Theft alerts
- `obc-rider-activity` - Ride history/statistics
- `navigation-routeservice` - Route planning
- `bcm-configuration-service` - Bike configuration

See `exploration/explore_lock_api.py` for lock/alarm API exploration script.

## Testing Lock/Alarm Sensors

To help improve lock/alarm sensors, we've added logging. When you:

- Enable/disable transport mode
- Lock/unlock the bike
- Enable/disable alarm

The logs will show:

```text
Lock status: is_locked=<value>, lock_enabled=<value>, alarm_enabled=<value>
```

This will help us understand how these fields behave and improve the sensors.
