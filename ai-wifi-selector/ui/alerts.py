"""
Desktop Alerts - Windows toast notifications
"""
import logging
from win10toast import ToastNotifier

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages desktop notifications"""
    
    def __init__(self):
        try:
            self.toaster = ToastNotifier()
            self.enabled = True
        except Exception as e:
            logger.error(f"Error initializing toast notifier: {e}")
            self.enabled = False
    
    def show_notification(self, title: str, message: str, duration: int = 5):
        """Show desktop notification"""
        if not self.enabled:
            logger.warning(f"Notifications disabled: {title} - {message}")
            return
        
        try:
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def notify_wifi_switch(self, old_ssid: str, new_ssid: str):
        """Notify about WiFi network switch"""
        self.show_notification(
            title="WiFi Switched",
            message=f"Switched from {old_ssid} to {new_ssid}",
            duration=5
        )
    
    def notify_connection_lost(self):
        """Notify about connection loss"""
        self.show_notification(
            title="Connection Lost",
            message="WiFi connection lost. Attempting to reconnect...",
            duration=5
        )
    
    def notify_connection_restored(self, ssid: str):
        """Notify about connection restoration"""
        self.show_notification(
            title="Connection Restored",
            message=f"Connected to {ssid}",
            duration=3
        )
    
    def notify_best_network_found(self, ssid: str, score: float):
        """Notify about best network found"""
        self.show_notification(
            title="Best Network Found",
            message=f"{ssid} (Score: {score:.1f})",
            duration=5
        )

