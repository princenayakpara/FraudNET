"""
Main Application Controller - Coordinates all components
"""
import sys
import os
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.wifi_scanner import WiFiScanner
from core.speed_tester import SpeedTester
from core.signal_analyzer import SignalAnalyzer
from core.network_switcher import NetworkSwitcher
from core.monitor import NetworkMonitor
from ai.predictor import WiFiPredictor
from ai.trainer import ModelTrainer
from db.database import Database
from ui.alerts import AlertManager
from api.server import APIServer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('logs', exist_ok=True)


class AppController:
    """Main application controller"""
    
    def __init__(self):
        # Core components
        self.scanner = WiFiScanner()
        self.speed_tester = SpeedTester()
        self.analyzer = SignalAnalyzer()
        self.switcher = NetworkSwitcher()
        self.predictor = WiFiPredictor()
        self.trainer = ModelTrainer()
        self.db = Database()
        self.alerts = AlertManager()
        
        # Monitoring
        self.monitor = NetworkMonitor(on_switch_callback=self._on_network_switch)
        self.monitoring = False
        
        # Training schedule
        self.last_training_time = None
        self.training_interval = 24 * 60 * 60  # 24 hours in seconds
        
        # Check if adapter is available
        if not self.scanner.check_adapter():
            logger.warning("WiFi adapter not detected. Some features may not work.")
    
    def _on_network_switch(self, ssid: str, reason: str):
        """Callback when network switches"""
        logger.info(f"Network switched to {ssid} ({reason})")
        self.alerts.notify_wifi_switch("Previous", ssid)
        
        # Log the switch
        self._log_network_metrics(ssid)
    
    def start_monitoring(self):
        """Start background monitoring"""
        if not self.monitoring:
            self.monitor.start_monitoring()
            self.monitoring = True
            logger.info("Background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self.monitoring:
            self.monitor.stop_monitoring()
            self.monitoring = False
            logger.info("Background monitoring stopped")
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self.monitoring
    
    def scan_networks(self) -> List[Dict]:
        """Scan for available networks"""
        return self.scanner.scan_networks()
    
    def get_current_connection(self) -> Optional[Dict]:
        """Get current WiFi connection"""
        return self.switcher.get_current_connection()
    
    def connect_to_network(self, ssid: str, password: str = None) -> Dict:
        """Connect to a specific network"""
        result = self.switcher.connect(ssid, password)
        
        if result.get("success"):
            self._log_network_metrics(ssid)
            self.alerts.notify_wifi_switch("Previous", ssid)
        
        return result
    
    def connect_to_best(self) -> Dict:
        """Connect to best available network using ML"""
        try:
            networks = self.scanner.scan_networks()
            if not networks:
                return {
                    "success": False,
                    "message": "No networks available"
                }
            
            # Get current speed metrics for prediction
            speed_result = self.speed_tester.ping_test()
            
            # Find best network
            if self.predictor:
                best_network = self.predictor.predict_best_network(networks, speed_result)
            else:
                # Fallback: use signal strength
                best_network = max(networks, key=lambda n: n.get("best_signal", 0))
                best_network["ml_score"] = best_network.get("best_signal", 0) * 0.8
            
            if not best_network:
                return {
                    "success": False,
                    "message": "Could not determine best network"
                }
            
            ssid = best_network.get("ssid")
            score = best_network.get("ml_score", 0)
            
            # Connect
            result = self.switcher.connect(ssid)
            
            if result.get("success"):
                self._log_network_metrics(ssid)
                self.alerts.notify_best_network_found(ssid, score)
            
            return {
                "success": result.get("success"),
                "message": result.get("message"),
                "ssid": ssid,
                "ml_score": score
            }
            
        except Exception as e:
            logger.error(f"Error connecting to best network: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def _log_network_metrics(self, ssid: str):
        """Log network metrics to database"""
        try:
            # Get network details
            network = self.scanner.get_network_details(ssid)
            if not network:
                return
            
            # Get current connection
            current = self.switcher.get_current_connection()
            if not current or current.get("ssid") != ssid:
                return
            
            # Perform speed test
            speed_result = self.speed_tester.full_test(use_cli=False)
            
            # Analyze signal
            analysis = self.analyzer.analyze_network(network)
            
            # Predict ML score
            network_data = {
                "ssid": ssid,
                "best_signal": network.get("best_signal", 0),
                "best_rssi": network.get("best_rssi", -100),
                "stability_score": analysis.get("stability_score", 50)
            }
            ml_score = self.predictor.predict_score(network_data, speed_result)
            
            # Calculate quality score
            quality_score = (
                network.get("best_signal", 0) * 0.3 +
                (100 - speed_result.get("ping_ms", 999) / 5) * 0.2 +
                (100 - speed_result.get("packet_loss_percent", 100)) * 0.2 +
                speed_result.get("download_mbps", 0) * 0.15 +
                analysis.get("stability_score", 50) * 0.15
            )
            
            # Save to database
            log_data = {
                "ssid": ssid,
                "bssid": network.get("bssids", [{}])[0].get("bssid") if network.get("bssids") else None,
                "rssi": network.get("best_rssi", -100),
                "signal_strength": network.get("best_signal", 0),
                "download_mbps": speed_result.get("download_mbps", 0),
                "upload_mbps": speed_result.get("upload_mbps", 0),
                "ping_ms": speed_result.get("ping_ms", 999),
                "packet_loss_percent": speed_result.get("packet_loss_percent", 0),
                "stability_score": analysis.get("stability_score", 50),
                "quality_score": quality_score,
                "ml_score": ml_score
            }
            
            self.db.add_log(log_data)
            logger.debug(f"Logged metrics for {ssid}")
            
        except Exception as e:
            logger.error(f"Error logging network metrics: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent network logs"""
        return self.db.get_recent_logs(hours=24, limit=limit)
    
    def train_model(self) -> Dict:
        """Train ML model"""
        try:
            result = self.trainer.train()
            if result.get("success"):
                # Reload predictor with new model
                self.predictor.load_model()
                self.last_training_time = datetime.utcnow()
            return result
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_model_info(self) -> Dict:
        """Get ML model information"""
        return self.trainer.get_model_info()
    
    def export_logs(self, filepath: str):
        """Export logs to file"""
        if filepath.endswith('.csv'):
            self.db.export_to_csv(filepath)
        elif filepath.endswith('.json'):
            self.db.export_to_json(filepath)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")
    
    def check_training_schedule(self):
        """Check if model needs retraining"""
        if self.last_training_time is None:
            # Train on first run if model doesn't exist
            if not self.trainer.model_exists():
                logger.info("No model found, training initial model...")
                self.train_model()
            return
        
        elapsed = (datetime.utcnow() - self.last_training_time).total_seconds()
        if elapsed >= self.training_interval:
            logger.info("24 hours elapsed, retraining model...")
            self.train_model()
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old logs"""
        deleted = self.db.delete_old_logs(days=days)
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old logs")


def main():
    """Main entry point"""
    try:
        # Create app controller
        controller = AppController()
        
        # Start API server
        api_server = APIServer(controller)
        api_server.start()
        
        # Start monitoring
        controller.start_monitoring()
        
        # Check training schedule
        controller.check_training_schedule()
        
        # Schedule periodic tasks
        def periodic_tasks():
            while True:
                time.sleep(3600)  # Every hour
                controller.check_training_schedule()
                controller.cleanup_old_logs()
        
        threading.Thread(target=periodic_tasks, daemon=True).start()
        
        # Keep main thread alive
        logger.info("AI WiFi Selector started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            controller.stop_monitoring()
            api_server.stop()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

