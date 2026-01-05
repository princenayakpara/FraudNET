"""
Main Entry Point - PyQt6 GUI Application
"""
import sys
import os
import logging
import threading
import time
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from app import AppController
from ui.dashboard import Dashboard
from ui.tray import TrayIcon
from api.server import APIServer

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WiFiSelectorApp:
    """Main application class"""
    
    def __init__(self):
        # Create app controller
        self.controller = AppController()
        
        # Create PyQt6 application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Don't quit when window closes
        
        # Create dashboard
        self.dashboard = Dashboard(self.controller)
        
        # Create tray icon
        self.tray = TrayIcon(
            on_quit_callback=self.quit,
            on_show_callback=self.show_dashboard
        )
        
        # Start API server
        self.api_server = APIServer(self.controller)
        self.api_server.start()
        
        # Start monitoring
        self.controller.start_monitoring()
        
        # Check training schedule
        self.controller.check_training_schedule()
        
        # Setup periodic tasks
        self.setup_periodic_tasks()
    
    def show_dashboard(self):
        """Show dashboard window"""
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
    
    def quit(self):
        """Quit application"""
        logger.info("Quitting application...")
        self.controller.stop_monitoring()
        self.api_server.stop()
        self.tray.stop()
        self.app.quit()
    
    def setup_periodic_tasks(self):
        """Setup periodic background tasks"""
        def periodic_tasks():
            while True:
                time.sleep(3600)  # Every hour
                try:
                    # Check training schedule
                    self.controller.check_training_schedule()
                    
                    # Cleanup old logs
                    self.controller.cleanup_old_logs()
                    
                    # Update tray tooltip
                    current = self.controller.get_current_connection()
                    if current:
                        ssid = current.get("ssid", "None")
                        signal = current.get("signal", 0)
                        self.tray.update_tooltip(f"AI WiFi Selector - {ssid} ({signal}%)")
                    else:
                        self.tray.update_tooltip("AI WiFi Selector - Not Connected")
                except Exception as e:
                    logger.error(f"Error in periodic tasks: {e}")
        
        threading.Thread(target=periodic_tasks, daemon=True).start()
    
    def run(self):
        """Run the application"""
        # Start tray icon
        self.tray.start()
        
        # Show dashboard initially
        self.show_dashboard()
        
        # Update tray tooltip
        current = self.controller.get_current_connection()
        if current:
            ssid = current.get("ssid", "None")
            signal = current.get("signal", 0)
            self.tray.update_tooltip(f"AI WiFi Selector - {ssid} ({signal}%)")
        else:
            self.tray.update_tooltip("AI WiFi Selector - Not Connected")
        
        logger.info("AI WiFi Selector GUI started")
        
        # Run PyQt6 event loop
        sys.exit(self.app.exec())


def main():
    """Main entry point"""
    try:
        app = WiFiSelectorApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

