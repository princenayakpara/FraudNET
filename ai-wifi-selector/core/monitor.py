"""
Background Monitor - Monitors network health and auto-switches when needed
"""
import time
import threading
import logging
from typing import Callable, Optional
from core.wifi_scanner import WiFiScanner
from core.speed_tester import SpeedTester
from core.signal_analyzer import SignalAnalyzer
from core.network_switcher import NetworkSwitcher
from ai.predictor import WiFiPredictor

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """Background monitoring and auto-switching"""
    
    def __init__(self, on_switch_callback: Optional[Callable] = None):
        self.scanner = WiFiScanner()
        self.speed_tester = SpeedTester()
        self.analyzer = SignalAnalyzer()
        self.switcher = NetworkSwitcher()
        self.predictor = WiFiPredictor() if WiFiPredictor else None
        
        self.monitoring = False
        self.monitor_thread = None
        self.check_interval = 60  # Check every 60 seconds
        self.on_switch_callback = on_switch_callback
        
        self.min_signal_threshold = 30  # Minimum signal strength
        self.min_speed_threshold = 1.0  # Minimum download speed in Mbps
        
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Network monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Network monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        consecutive_failures = 0
        max_failures = 3
        
        while self.monitoring:
            try:
                # Check if adapter is available
                if not self.scanner.check_adapter():
                    logger.warning("WiFi adapter not available")
                    time.sleep(10)
                    continue
                
                # Get current connection
                current = self.switcher.get_current_connection()
                
                if not current:
                    logger.info("Not connected to any network, attempting to connect...")
                    self._auto_connect_best()
                    time.sleep(self.check_interval)
                    continue
                
                # Test current connection
                current_ssid = current.get("ssid")
                signal = current.get("signal", 0)
                
                # Quick speed test
                speed_result = self.speed_tester.ping_test()
                ping = speed_result.get("ping_ms", 999)
                packet_loss = speed_result.get("packet_loss_percent", 0)
                
                # Check if connection is poor
                is_poor = (
                    signal < self.min_signal_threshold or
                    ping > 200 or
                    packet_loss > 10
                )
                
                if is_poor:
                    consecutive_failures += 1
                    logger.warning(
                        f"Poor connection detected: Signal={signal}%, Ping={ping}ms, Loss={packet_loss}%"
                    )
                    
                    if consecutive_failures >= max_failures:
                        logger.info("Attempting to switch to better network...")
                        self._auto_switch()
                        consecutive_failures = 0
                else:
                    consecutive_failures = 0
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(self.check_interval)
    
    def _auto_connect_best(self):
        """Automatically connect to the best available network"""
        try:
            networks = self.scanner.scan_networks()
            if not networks:
                return
            
            # Use ML predictor to find best network
            best_network = self._find_best_network(networks)
            
            if best_network:
                ssid = best_network.get("ssid")
                logger.info(f"Auto-connecting to best network: {ssid}")
                result = self.switcher.connect(ssid)
                
                if result["success"] and self.on_switch_callback:
                    self.on_switch_callback(ssid, "auto-connect")
        
        except Exception as e:
            logger.error(f"Error in auto-connect: {e}")
    
    def _auto_switch(self):
        """Automatically switch to a better network"""
        try:
            current = self.switcher.get_current_connection()
            if not current:
                self._auto_connect_best()
                return
            
            current_ssid = current.get("ssid")
            networks = self.scanner.scan_networks()
            
            if not networks:
                return
            
            # Find best network (excluding current)
            available_networks = [n for n in networks if n.get("ssid") != current_ssid]
            
            if not available_networks:
                return
            
            best_network = self._find_best_network(available_networks)
            
            if best_network:
                best_ssid = best_network.get("ssid")
                best_score = best_network.get("ml_score", 0)
                
                # Get current network score for comparison
                current_network_data = {
                    "ssid": current_ssid,
                    "best_signal": current.get("signal", 0),
                    "best_rssi": -100 + (current.get("signal", 0) * 0.5)
                }
                current_score = self.predictor.predict_score(current_network_data, {})
                
                # Only switch if significantly better (20% improvement)
                if best_score > current_score * 1.2:
                    logger.info(
                        f"Switching from {current_ssid} (score: {current_score:.2f}) "
                        f"to {best_ssid} (score: {best_score:.2f})"
                    )
                    
                    result = self.switcher.connect(best_ssid)
                    
                    if result["success"] and self.on_switch_callback:
                        self.on_switch_callback(best_ssid, "auto-switch")
                else:
                    logger.info("No significantly better network found")
        
        except Exception as e:
            logger.error(f"Error in auto-switch: {e}")
    
    def _find_best_network(self, networks):
        """Find best network using ML predictor"""
        if not networks:
            return None
        
        best_network = None
        best_score = -1
        
        # Quick speed test for current conditions
        speed_result = self.speed_tester.ping_test()
        
        for network in networks:
            try:
                # Predict score for this network
                network_data = {
                    "ssid": network.get("ssid"),
                    "best_signal": network.get("best_signal", 0),
                    "best_rssi": network.get("best_rssi", -100)
                }
                
                # Use current speed metrics as baseline
                metrics = {
                    "download_mbps": 10.0,  # Default estimate
                    "upload_mbps": 5.0,
                    "ping_ms": speed_result.get("ping_ms", 50),
                    "packet_loss_percent": speed_result.get("packet_loss_percent", 0)
                }
                
                if self.predictor:
                    score = self.predictor.predict_score(network_data, metrics)
                else:
                    # Fallback: use signal strength as score
                    score = network.get("best_signal", 0)
                network["ml_score"] = score
                
                if score > best_score:
                    best_score = score
                    best_network = network
            
            except Exception as e:
                logger.error(f"Error predicting score for {network.get('ssid')}: {e}")
                continue
        
        return best_network
    
    def force_check(self):
        """Manually trigger a network check and potential switch"""
        if self.monitoring:
            self._auto_switch()

