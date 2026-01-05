"""
PyQt6 Dashboard - Main application UI
"""
import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
    QTabWidget, QGroupBox, QProgressBar, QMessageBox, QLineEdit
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
import threading

logger = logging.getLogger(__name__)


class ScanThread(QThread):
    """Thread for scanning networks without blocking UI"""
    networks_scanned = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner
    
    def run(self):
        try:
            networks = self.scanner.scan_networks()
            self.networks_scanned.emit(networks)
        except Exception as e:
            self.error_occurred.emit(str(e))


class Dashboard(QMainWindow):
    """Main dashboard window"""
    
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.init_ui()
        self.setup_timers()
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("AI WiFi Selector")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("AI WiFi Selector")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("padding: 5px; background: #e0e0e0; border-radius: 5px;")
        status_layout.addWidget(self.status_label)
        
        # Current connection
        self.current_network_label = QLabel("Connected: None")
        self.current_network_label.setStyleSheet("padding: 5px; background: #d0f0d0; border-radius: 5px;")
        status_layout.addWidget(self.current_network_label)
        
        main_layout.addLayout(status_layout)
        
        # Tabs
        tabs = QTabWidget()
        
        # Networks tab
        networks_tab = self.create_networks_tab()
        tabs.addTab(networks_tab, "Networks")
        
        # Logs tab
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "Logs")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        main_layout.addWidget(tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("Scan Networks")
        self.scan_btn.clicked.connect(self.scan_networks)
        button_layout.addWidget(self.scan_btn)
        
        self.connect_btn = QPushButton("Connect to Best")
        self.connect_btn.clicked.connect(self.connect_best)
        button_layout.addWidget(self.connect_btn)
        
        self.train_btn = QPushButton("Train Model")
        self.train_btn.clicked.connect(self.train_model)
        button_layout.addWidget(self.train_btn)
        
        self.export_btn = QPushButton("Export Logs")
        self.export_btn.clicked.connect(self.export_logs)
        button_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_networks_tab(self):
        """Create networks tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Networks table
        self.networks_table = QTableWidget()
        self.networks_table.setColumnCount(6)
        self.networks_table.setHorizontalHeaderLabels([
            "SSID", "Signal", "RSSI", "Security", "ML Score", "Action"
        ])
        self.networks_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.networks_table)
        
        return widget
    
    def create_logs_tab(self):
        """Create logs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(8)
        self.logs_table.setHorizontalHeaderLabels([
            "Time", "SSID", "Signal", "Download", "Upload", "Ping", "Loss", "Score"
        ])
        layout.addWidget(self.logs_table)
        
        return widget
    
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Monitoring settings
        monitor_group = QGroupBox("Monitoring")
        monitor_layout = QVBoxLayout()
        
        self.monitor_enabled = QPushButton("Monitoring: ON")
        self.monitor_enabled.setCheckable(True)
        self.monitor_enabled.setChecked(True)
        self.monitor_enabled.clicked.connect(self.toggle_monitoring)
        monitor_layout.addWidget(self.monitor_enabled)
        
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)
        
        # Model info
        model_group = QGroupBox("ML Model")
        model_layout = QVBoxLayout()
        
        self.model_status = QLabel("Model: Not loaded")
        model_layout.addWidget(self.model_status)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        layout.addStretch()
        
        return widget
    
    def setup_timers(self):
        """Setup update timers"""
        # Update current connection every 5 seconds
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.update_current_connection)
        self.connection_timer.start(5000)
        
        # Update logs every 10 seconds
        self.logs_timer = QTimer()
        self.logs_timer.timeout.connect(self.update_logs)
        self.logs_timer.start(10000)
        
        # Initial updates
        self.update_current_connection()
        self.update_logs()
    
    def scan_networks(self):
        """Scan for WiFi networks"""
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        self.status_label.setText("Status: Scanning networks...")
        
        # Run scan in thread
        self.scan_thread = ScanThread(self.app_controller.scanner)
        self.scan_thread.networks_scanned.connect(self.on_networks_scanned)
        self.scan_thread.error_occurred.connect(self.on_scan_error)
        self.scan_thread.start()
    
    def on_networks_scanned(self, networks):
        """Handle scanned networks"""
        self.networks_table.setRowCount(len(networks))
        
        for i, network in enumerate(networks):
            ssid = network.get("ssid", "Unknown")
            signal = network.get("best_signal", 0)
            rssi = network.get("best_rssi", -100)
            auth = network.get("auth", "Unknown")
            ml_score = network.get("ml_score", 0)
            
            self.networks_table.setItem(i, 0, QTableWidgetItem(ssid))
            self.networks_table.setItem(i, 1, QTableWidgetItem(f"{signal}%"))
            self.networks_table.setItem(i, 2, QTableWidgetItem(f"{rssi:.1f} dBm"))
            self.networks_table.setItem(i, 3, QTableWidgetItem(auth))
            self.networks_table.setItem(i, 4, QTableWidgetItem(f"{ml_score:.2f}"))
            
            connect_btn = QPushButton("Connect")
            connect_btn.clicked.connect(lambda checked, s=ssid: self.connect_to_network(s))
            self.networks_table.setCellWidget(i, 5, connect_btn)
        
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan Networks")
        self.status_label.setText(f"Status: Found {len(networks)} networks")
    
    def on_scan_error(self, error_msg):
        """Handle scan error"""
        QMessageBox.warning(self, "Scan Error", f"Error scanning networks: {error_msg}")
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan Networks")
        self.status_label.setText("Status: Scan failed")
    
    def connect_to_network(self, ssid: str):
        """Connect to a specific network"""
        result = self.app_controller.connect_to_network(ssid)
        if result.get("success"):
            QMessageBox.information(self, "Connected", f"Connected to {ssid}")
            self.update_current_connection()
        else:
            QMessageBox.warning(self, "Connection Failed", result.get("message", "Unknown error"))
    
    def connect_best(self):
        """Connect to best network"""
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        result = self.app_controller.connect_to_best()
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect to Best")
        
        if result.get("success"):
            QMessageBox.information(self, "Connected", f"Connected to {result.get('ssid')}")
        else:
            QMessageBox.warning(self, "Connection Failed", result.get("message", "Unknown error"))
    
    def train_model(self):
        """Train ML model"""
        self.train_btn.setEnabled(False)
        self.train_btn.setText("Training...")
        self.status_label.setText("Status: Training model...")
        
        # Run in thread to avoid blocking
        def train():
            result = self.app_controller.train_model()
            self.train_btn.setEnabled(True)
            self.train_btn.setText("Train Model")
            if result.get("success"):
                self.status_label.setText("Status: Model trained successfully")
                QMessageBox.information(self, "Training Complete", "Model trained successfully!")
            else:
                self.status_label.setText("Status: Training failed")
                QMessageBox.warning(self, "Training Failed", result.get("message", "Unknown error"))
        
        threading.Thread(target=train, daemon=True).start()
    
    def export_logs(self):
        """Export logs to CSV/JSON"""
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if filepath:
            self.app_controller.export_logs(filepath)
            QMessageBox.information(self, "Export Complete", f"Logs exported to {filepath}")
    
    def update_current_connection(self):
        """Update current connection display"""
        current = self.app_controller.get_current_connection()
        if current:
            ssid = current.get("ssid", "Unknown")
            signal = current.get("signal", 0)
            self.current_network_label.setText(f"Connected: {ssid} ({signal}%)")
        else:
            self.current_network_label.setText("Connected: None")
    
    def update_logs(self):
        """Update logs table"""
        logs = self.app_controller.get_recent_logs(limit=50)
        self.logs_table.setRowCount(len(logs))
        
        for i, log in enumerate(logs):
            timestamp = log.get("timestamp", "")[:19] if log.get("timestamp") else ""
            self.logs_table.setItem(i, 0, QTableWidgetItem(timestamp))
            self.logs_table.setItem(i, 1, QTableWidgetItem(log.get("ssid", "")))
            self.logs_table.setItem(i, 2, QTableWidgetItem(str(log.get("signal_strength", 0))))
            self.logs_table.setItem(i, 3, QTableWidgetItem(f"{log.get('download_mbps', 0):.2f}"))
            self.logs_table.setItem(i, 4, QTableWidgetItem(f"{log.get('upload_mbps', 0):.2f}"))
            self.logs_table.setItem(i, 5, QTableWidgetItem(f"{log.get('ping_ms', 0):.2f}"))
            self.logs_table.setItem(i, 6, QTableWidgetItem(f"{log.get('packet_loss_percent', 0):.2f}"))
            self.logs_table.setItem(i, 7, QTableWidgetItem(f"{log.get('ml_score', 0):.2f}"))
    
    def toggle_monitoring(self):
        """Toggle background monitoring"""
        if self.monitor_enabled.isChecked():
            self.app_controller.start_monitoring()
            self.monitor_enabled.setText("Monitoring: ON")
        else:
            self.app_controller.stop_monitoring()
            self.monitor_enabled.setText("Monitoring: OFF")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Minimize to tray instead of closing
        self.hide()
        event.ignore()

