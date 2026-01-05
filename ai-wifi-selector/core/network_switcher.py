"""
Network Switcher - Handles WiFi connection switching
"""
import subprocess
import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class NetworkSwitcher:
    """Manages WiFi network connections"""
    
    def __init__(self):
        self.current_ssid = None
        self.connection_attempts = {}
        self.max_attempts = 3
        
    def connect(self, ssid: str, password: str = None) -> Dict:
        """
        Connect to a WiFi network
        Returns: {success: bool, message: str, ssid: str}
        """
        try:
            # Check if already connected to this network
            current = self.get_current_connection()
            if current and current.get("ssid") == ssid:
                return {
                    "success": True,
                    "message": f"Already connected to {ssid}",
                    "ssid": ssid
                }
            
            # Build netsh command
            if password:
                # Connect with password
                cmd = [
                    "netsh", "wlan", "connect", 
                    f"name={ssid}",
                    f"ssid={ssid}",
                    f"key={password}"
                ]
            else:
                # Connect without password (open network or saved profile)
                cmd = ["netsh", "wlan", "connect", f"name={ssid}"]
            
            # Execute connection
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Wait a moment for connection to establish
            time.sleep(3)
            
            # Verify connection
            current = self.get_current_connection()
            if current and current.get("ssid") == ssid:
                self.current_ssid = ssid
                return {
                    "success": True,
                    "message": f"Successfully connected to {ssid}",
                    "ssid": ssid
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to connect to {ssid}",
                    "ssid": ssid
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": f"Connection to {ssid} timed out",
                "ssid": ssid
            }
        except Exception as e:
            logger.error(f"Error connecting to {ssid}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "ssid": ssid
            }
    
    def disconnect(self) -> Dict:
        """Disconnect from current WiFi network"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "disconnect"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            time.sleep(2)
            self.current_ssid = None
            
            return {
                "success": result.returncode == 0,
                "message": "Disconnected" if result.returncode == 0 else "Disconnect failed"
            }
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def get_current_connection(self) -> Optional[Dict]:
        """Get currently connected network information"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            connection = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if 'ssid' in key and 'bssid' not in key:
                        connection['ssid'] = value
                    elif 'signal' in key:
                        import re
                        match = re.search(r'(\d+)%', value)
                        if match:
                            connection['signal'] = int(match.group(1))
                    elif 'state' in key:
                        connection['state'] = value
                    elif 'bssid' in key:
                        connection['bssid'] = value
            
            if connection.get('ssid'):
                self.current_ssid = connection['ssid']
                return connection
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current connection: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if currently connected to any WiFi network"""
        connection = self.get_current_connection()
        return connection is not None and connection.get('state', '').lower() == 'connected'
    
    def connect_with_retry(self, ssid: str, password: str = None, max_retries: int = 3) -> Dict:
        """Connect with retry logic"""
        for attempt in range(1, max_retries + 1):
            logger.info(f"Connection attempt {attempt}/{max_retries} to {ssid}")
            result = self.connect(ssid, password)
            
            if result["success"]:
                return result
            
            if attempt < max_retries:
                time.sleep(2)  # Wait before retry
        
        return result

