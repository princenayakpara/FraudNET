"""
WiFi Scanner - Scans available WiFi networks using Windows netsh commands
"""
import subprocess
import re
import json
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WiFiScanner:
    """Scans and parses WiFi networks from Windows netsh output"""
    
    def __init__(self):
        self.last_scan_time = 0
        self.scan_cache = []
        self.cache_duration = 5  # Cache for 5 seconds
        
    def check_adapter(self) -> bool:
        """Check if WiFi adapter is available"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "State" in result.stdout and "connected" in result.stdout.lower()
        except Exception as e:
            logger.error(f"Error checking adapter: {e}")
            return False
    
    def scan_networks(self) -> List[Dict]:
        """
        Scan all available WiFi networks
        Returns list of network dictionaries with SSID, BSSID, signal strength, etc.
        """
        current_time = time.time()
        
        # Return cached results if recent
        if current_time - self.last_scan_time < self.cache_duration and self.scan_cache:
            return self.scan_cache
        
        networks = []
        
        try:
            # Run netsh command to get networks with BSSID info
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"netsh command failed: {result.stderr}")
                return networks
            
            output = result.stdout
            
            # Parse network information
            current_network = {}
            current_bssid = None
            
            for line in output.split('\n'):
                line = line.strip()
                
                # New network section
                if line.startswith("SSID"):
                    if current_network and current_bssid:
                        networks.append(current_network.copy())
                    
                    ssid_match = re.search(r'SSID \d+ : (.+)', line)
                    if ssid_match:
                        current_network = {
                            "ssid": ssid_match.group(1),
                            "bssids": [],
                            "auth": "",
                            "encryption": "",
                            "network_type": ""
                        }
                        current_bssid = None
                
                # Network type
                elif line.startswith("Network type"):
                    match = re.search(r'Network type\s*:\s*(.+)', line)
                    if match and current_network:
                        current_network["network_type"] = match.group(1).strip()
                
                # Authentication
                elif line.startswith("Authentication"):
                    match = re.search(r'Authentication\s*:\s*(.+)', line)
                    if match and current_network:
                        current_network["auth"] = match.group(1).strip()
                
                # Encryption
                elif line.startswith("Encryption"):
                    match = re.search(r'Encryption\s*:\s*(.+)', line)
                    if match and current_network:
                        current_network["encryption"] = match.group(1).strip()
                
                # BSSID entry
                elif line.startswith("BSSID"):
                    match = re.search(r'BSSID \d+\s*:\s*([a-fA-F0-9:]+)', line)
                    if match:
                        current_bssid = {
                            "bssid": match.group(1).strip(),
                            "signal": 0,
                            "radio_type": "",
                            "channel": 0
                        }
                        if current_network:
                            current_network["bssids"].append(current_bssid)
                
                # Signal strength
                elif line.startswith("Signal") and current_bssid:
                    match = re.search(r'Signal\s*:\s*(\d+)%', line)
                    if match:
                        current_bssid["signal"] = int(match.group(1))
                
                # Radio type
                elif line.startswith("Radio type") and current_bssid:
                    match = re.search(r'Radio type\s*:\s*(.+)', line)
                    if match:
                        current_bssid["radio_type"] = match.group(1).strip()
                
                # Channel
                elif line.startswith("Channel") and current_bssid:
                    match = re.search(r'Channel\s*:\s*(\d+)', line)
                    if match:
                        current_bssid["channel"] = int(match.group(1))
            
            # Add last network
            if current_network and current_network.get("bssids"):
                networks.append(current_network)
            
            # Convert signal percentage to RSSI (approximate)
            for network in networks:
                for bssid in network.get("bssids", []):
                    signal_pct = bssid.get("signal", 0)
                    # Convert percentage to RSSI (0% = -100dBm, 100% = -50dBm)
                    bssid["rssi"] = -100 + (signal_pct * 0.5)
            
            # Sort by best signal
            for network in networks:
                if network.get("bssids"):
                    network["bssids"].sort(key=lambda x: x.get("signal", 0), reverse=True)
                    network["best_signal"] = network["bssids"][0].get("signal", 0)
                    network["best_rssi"] = network["bssids"][0].get("rssi", -100)
            
            networks.sort(key=lambda x: x.get("best_signal", 0), reverse=True)
            
            self.scan_cache = networks
            self.last_scan_time = current_time
            
        except subprocess.TimeoutExpired:
            logger.error("WiFi scan timed out")
        except Exception as e:
            logger.error(f"Error scanning networks: {e}")
        
        return networks
    
    def get_current_network(self) -> Optional[Dict]:
        """Get currently connected WiFi network"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            current = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'ssid' in key:
                        current['ssid'] = value
                    elif 'signal' in key:
                        match = re.search(r'(\d+)%', value)
                        if match:
                            current['signal'] = int(match.group(1))
                            current['rssi'] = -100 + (current['signal'] * 0.5)
            
            return current if current.get('ssid') else None
            
        except Exception as e:
            logger.error(f"Error getting current network: {e}")
            return None
    
    def get_network_details(self, ssid: str) -> Optional[Dict]:
        """Get detailed information about a specific network"""
        networks = self.scan_networks()
        for network in networks:
            if network.get("ssid") == ssid:
                return network
        return None

