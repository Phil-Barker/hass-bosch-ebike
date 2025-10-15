#!/usr/bin/env python3
"""
Battery Status Monitor

Polls the bike-profile endpoint to check for live battery data.
Run this while your bike is on to see when live data appears.
"""

import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

import requests


class BatteryMonitor:
    """Monitor battery status from Bosch Flow API."""
    
    def __init__(self, token_file: str = "tokens.json"):
        """Initialize with Flow API tokens."""
        self.access_token = None
        self.refresh_token = None
        self.token_file = token_file
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Flow/56 CFNetwork/1240.0.4 Darwin/20.6.0",
            "Accept-Language": "de-de",
        })
        
        self.load_tokens()
        self.refresh_token_if_needed()
    
    def load_tokens(self):
        """Load tokens from file."""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
    
    def refresh_token_if_needed(self):
        """Try to refresh the access token."""
        if not self.refresh_token:
            return False
        
        data = {
            "refresh_token": self.refresh_token,
            "client_id": "one-bike-app",
            "grant_type": "refresh_token",
        }
        
        try:
            response = self.session.post(
                "https://p9.authz.bosch.com/auth/realms/obc/protocol/openid-connect/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"✗ Token refresh failed: {e}")
            return False
    
    def get_bike_profile(self, bike_id: str) -> Optional[Dict[str, Any]]:
        """Get bike profile data."""
        url = f"https://obc-rider-profile.prod.connected-biking.cloud/v1/bike-profile/{bike_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Error: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def get_state_of_charge(self, bike_id: str) -> Optional[Dict[str, Any]]:
        """Get state of charge data (from ConnectModule)."""
        url = f"https://obc-rider-profile.prod.connected-biking.cloud/v1/state-of-charge/{bike_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None
    
    def extract_battery_info(self, profile_data: Dict[str, Any], soc_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract battery information from profile data and state-of-charge."""
        try:
            battery = profile_data["data"]["attributes"]["batteries"][0]
            drive_unit = profile_data["data"]["attributes"]["driveUnit"]
            
            info = {
                "timestamp": datetime.now().isoformat(),
                "battery": {
                    "level_percent": battery.get("batteryLevel"),
                    "remaining_wh": battery.get("remainingEnergy"),
                    "total_capacity_wh": battery.get("totalEnergy"),
                    "is_charging": battery.get("isCharging"),
                    "is_charger_connected": battery.get("isChargerConnected"),
                    "is_light_reserve": battery.get("isLightReserveReached"),
                    "charge_cycles_total": battery.get("numberOfFullChargeCycles", {}).get("total"),
                    "delivered_lifetime_wh": battery.get("deliveredWhOverLifetime"),
                },
                "bike": {
                    "total_distance_m": drive_unit.get("totalDistanceTraveled"),
                    "is_locked": drive_unit.get("lock", {}).get("isLocked"),
                    "light_on": drive_unit.get("bikeLight", {}).get("isSwitchedOn"),
                },
                "soc_data": None
            }
            
            # If we have state-of-charge data, add it
            if soc_data:
                info["soc_data"] = {
                    "state_of_charge": soc_data.get("stateOfCharge"),
                    "charger_connected": soc_data.get("chargerConnected"),
                    "charging_active": soc_data.get("chargingActive"),
                    "remaining_energy": soc_data.get("remainingEnergyForRider"),
                    "reachable_range": soc_data.get("reachableRange"),
                    "odometer": soc_data.get("odometer"),
                    "last_update": soc_data.get("stateOfChargeLatestUpdate"),
                }
                
                # Use SoC data to fill in profile nulls
                if info["battery"]["level_percent"] is None and soc_data.get("stateOfCharge") is not None:
                    info["battery"]["level_percent"] = soc_data.get("stateOfCharge")
                
                if info["battery"]["is_charging"] is None and soc_data.get("chargingActive") is not None:
                    info["battery"]["is_charging"] = soc_data.get("chargingActive")
                
                if info["battery"]["is_charger_connected"] is None and soc_data.get("chargerConnected") is not None:
                    info["battery"]["is_charger_connected"] = soc_data.get("chargerConnected")
            
            return info
        except (KeyError, IndexError, TypeError) as e:
            print(f"✗ Error extracting data: {e}")
            return None
    
    def display_battery_status(self, info: Dict[str, Any]):
        """Display battery status in a nice format."""
        battery = info["battery"]
        bike = info["bike"]
        soc = info.get("soc_data")
        
        print(f"\n{'='*70}")
        print(f"Battery Status @ {info['timestamp']}")
        print(f"{'='*70}")
        
        # Live data status - check both sources
        has_live_data = battery["level_percent"] is not None
        has_soc_data = soc is not None and soc.get("state_of_charge") is not None
        
        if has_live_data or has_soc_data:
            print(f"🔋 LIVE DATA AVAILABLE! 🎉\n")
            print(f"Battery Level:      {battery['level_percent']}%")
            
            if battery['remaining_wh'] is not None:
                print(f"Remaining Energy:   {battery['remaining_wh']:.1f} Wh")
            elif soc and soc.get('remaining_energy') is not None:
                print(f"Remaining Energy:   {soc['remaining_energy']:.1f} Wh (from ConnectModule)")
            
            print(f"Total Capacity:     {battery['total_capacity_wh']:.1f} Wh")
            
            if battery["is_charging"] is not None:
                charging_status = "⚡ CHARGING" if battery["is_charging"] else "Not charging"
                print(f"Charging:           {charging_status}")
            
            if battery["is_charger_connected"] is not None:
                charger = "Yes" if battery["is_charger_connected"] else "No"
                print(f"Charger connected:  {charger}")
            
            # Show SoC-specific data
            if soc:
                print(f"\n📡 ConnectModule Data:")
                if soc.get("reachable_range"):
                    ranges = soc["reachable_range"]
                    print(f"Reachable Range:    {ranges} km (per assist mode)")
                if soc.get("last_update"):
                    print(f"Last Update:        {soc['last_update']}")
        else:
            print(f"⚠️  No live data (bike offline)\n")
            print(f"Total Capacity:     {battery['total_capacity_wh']:.1f} Wh (max)")
        
        print(f"\nLifetime Stats:")
        print(f"Charge Cycles:      {battery['charge_cycles_total']:.1f}")
        print(f"Energy Delivered:   {battery['delivered_lifetime_wh']:,} Wh")
        
        if soc and soc.get("odometer"):
            print(f"Total Distance:     {soc['odometer']/1000:.1f} km (from ConnectModule)")
        else:
            print(f"Total Distance:     {bike['total_distance_m']/1000:.1f} km")
        
        if bike["is_locked"] is not None:
            lock_status = "🔒 LOCKED" if bike["is_locked"] else "🔓 Unlocked"
            print(f"Lock Status:        {lock_status}")
        
        print(f"{'='*70}\n")
        
        return has_live_data or has_soc_data
    
    def monitor_continuous(self, bike_id: str, interval: int = 60):
        """Monitor battery status continuously."""
        print(f"Starting battery monitor...")
        print(f"Checking every {interval} seconds")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Fetch both endpoints
                profile = self.get_bike_profile(bike_id)
                soc_data = self.get_state_of_charge(bike_id)
                
                if profile:
                    info = self.extract_battery_info(profile, soc_data)
                    if info:
                        has_live = self.display_battery_status(info)
                        
                        if has_live:
                            # Save the live data
                            filename = f"battery_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            with open(filename, 'w') as f:
                                json.dump(info, f, indent=2)
                            print(f"✓ Live data saved to {filename}\n")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    
    def check_once(self, bike_id: str, save: bool = True):
        """Check battery status once."""
        # Fetch both endpoints
        profile = self.get_bike_profile(bike_id)
        soc_data = self.get_state_of_charge(bike_id)
        
        if profile:
            info = self.extract_battery_info(profile, soc_data)
            if info:
                has_live = self.display_battery_status(info)
                
                if save:
                    filename = "latest_battery_status.json"
                    with open(filename, 'w') as f:
                        json.dump(info, f, indent=2)
                    
                    if has_live:
                        print(f"✓ Live data saved to {filename}")
                    else:
                        print(f"ℹ️  Status saved to {filename} (no live data yet)")
                
                return info
        
        return None


def main():
    """Main function."""
    import sys
    
    print("="*70)
    print("BOSCH EBIKE - BATTERY STATUS MONITOR")
    print("="*70 + "\n")
    
    if not os.path.exists("tokens.json"):
        print("✗ No tokens.json found")
        return
    
    monitor = BatteryMonitor()
    
    if not monitor.access_token:
        print("✗ No access token")
        return
    
    bike_id = "93763069-4373-4f85-b0ee-4a7993b8739b"
    
    # Check if monitoring mode requested
    if len(sys.argv) > 1 and sys.argv[1] in ["monitor", "watch", "continuous"]:
        interval = 60  # Default 60 seconds
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                pass
        
        monitor.monitor_continuous(bike_id, interval)
    else:
        # Single check
        print("Checking battery status once...")
        print("(Use 'python3 monitor_battery.py monitor' for continuous monitoring)\n")
        
        monitor.check_once(bike_id, save=True)
        
        print("\nTips:")
        print("  • Turn on your ebike OR plug in charger for live battery data")
        print("  • Run 'python3 monitor_battery.py monitor' to check continuously")
        print("  • ConnectModule sends updates every 5 minutes when charging")
        print("  • Checks both bike-profile and state-of-charge endpoints")


if __name__ == "__main__":
    main()

