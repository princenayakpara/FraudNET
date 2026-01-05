"""
System Tray - Tray icon and menu
"""
import sys
import pystray
from PIL import Image, ImageDraw
import threading
import logging

logger = logging.getLogger(__name__)


class TrayIcon:
    """System tray icon and menu"""
    
    def __init__(self, on_quit_callback=None, on_show_callback=None):
        self.on_quit = on_quit_callback
        self.on_show = on_show_callback
        self.icon = None
        self.running = False
    
    def create_image(self, width=64, height=64):
        """Create tray icon image"""
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw WiFi icon (simplified)
        # Draw signal waves
        draw.arc([20, 20, 44, 44], start=45, end=135, fill='blue', width=3)
        draw.arc([15, 15, 49, 49], start=45, end=135, fill='blue', width=3)
        draw.arc([10, 10, 54, 54], start=45, end=135, fill='blue', width=3)
        
        return image
    
    def create_menu(self):
        """Create tray menu"""
        menu_items = []
        
        if self.on_show:
            menu_items.append(
                pystray.MenuItem("Show Dashboard", self.on_show)
            )
        
        menu_items.append(pystray.MenuItem("---", None))
        
        if self.on_quit:
            menu_items.append(
                pystray.MenuItem("Quit", self.on_quit)
            )
        
        return pystray.Menu(*menu_items)
    
    def start(self):
        """Start tray icon"""
        try:
            image = self.create_image()
            menu = self.create_menu()
            
            self.icon = pystray.Icon("AI WiFi Selector", image, "AI WiFi Selector", menu)
            self.running = True
            
            # Run in separate thread
            thread = threading.Thread(target=self.icon.run, daemon=True)
            thread.start()
            
            logger.info("Tray icon started")
        except Exception as e:
            logger.error(f"Error starting tray icon: {e}")
    
    def stop(self):
        """Stop tray icon"""
        self.running = False
        if self.icon:
            self.icon.stop()
        logger.info("Tray icon stopped")
    
    def update_tooltip(self, text: str):
        """Update tray icon tooltip"""
        if self.icon:
            self.icon.title = text

