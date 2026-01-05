# AI WiFi Selector

A complete Windows Desktop Application that automatically connects to the best available WiFi network using machine learning.

## Features

- **WiFi Scanning**: Scan all nearby WiFi networks with signal strength, RSSI, and security info
- **Speed Testing**: Measure download, upload, ping, and packet loss
- **ML Prediction**: Uses RandomForestRegressor to predict best WiFi network
- **Auto-Switching**: Automatically switches to best network when connection degrades
- **Background Monitoring**: Continuous monitoring with auto-recovery
- **SQLite Logging**: Stores all network metrics in database
- **PyQt6 Dashboard**: Modern desktop UI with real-time updates
- **System Tray**: Minimize to tray with notifications
- **REST API**: FastAPI server for programmatic access
- **Export**: Export logs to CSV/JSON
- **Auto-Training**: Retrains ML model every 24 hours

## Installation

1. Install Python 3.10 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### GUI Mode
Run `main.py` for the full PyQt6 GUI with dashboard, system tray, and notifications.

### API Mode
Run `app.py` for headless mode with REST API only.

### API Endpoints

- `GET /api/status` - Get application status
- `GET /api/networks` - Get available WiFi networks
- `POST /api/switch` - Switch to a network
- `GET /api/logs` - Get network logs
- `GET /api/current` - Get current connection
- `POST /api/scan` - Trigger network scan
- `POST /api/best` - Connect to best network
- `GET /api/model/info` - Get ML model info
- `POST /api/model/train` - Train ML model

## Building Windows Executable

Build using PyInstaller:

```bash
pyinstaller --onefile --noconsole --name "AI-WiFi-Selector" main.py
```

Or use the provided spec file:

```bash
pyinstaller AI-WiFi-Selector.spec
```

## Project Structure

```
ai-wifi-selector/
├── app.py                 # Main application controller
├── main.py                # PyQt6 GUI entry point
├── requirements.txt       # Python dependencies
│
├── core/                  # Core WiFi operations
│   ├── wifi_scanner.py   # Network scanning
│   ├── speed_tester.py    # Speed testing
│   ├── signal_analyzer.py # Signal analysis
│   ├── network_switcher.py # Connection management
│   └── monitor.py         # Background monitoring
│
├── ai/                    # Machine learning
│   ├── dataset_builder.py # Build training dataset
│   ├── trainer.py         # Model training
│   └── predictor.py       # Network prediction
│
├── ui/                    # User interface
│   ├── dashboard.py       # PyQt6 dashboard
│   ├── tray.py            # System tray icon
│   └── alerts.py          # Desktop notifications
│
├── db/                    # Database
│   ├── database.py        # Database operations
│   └── models.py          # SQLAlchemy models
│
├── api/                   # REST API
│   ├── server.py          # FastAPI server
│   └── routes.py          # API routes
│
├── logs/                  # Application logs
└── models/                # Saved ML models
```

## ML Model

The application uses **RandomForestRegressor** from scikit-learn to predict WiFi quality scores.

**Input Features:**
- RSSI (signal strength in dBm)
- Download Speed (Mbps)
- Upload Speed (Mbps)
- Ping (ms)
- Packet Loss (%)
- Stability Score

**Output:**
- Quality Score (0-100, higher is better)

The model is automatically retrained every 24 hours using historical network logs.

## Requirements

- Windows 10/11
- Python 3.10+
- WiFi adapter
- Administrator privileges (for network switching)

## Error Handling

- Handles no WiFi adapter gracefully
- Retry logic on connection failures
- Auto-recovery from connection loss
- Graceful degradation if ML model unavailable

## License

MIT License

## Author

AI WiFi Selector - Automated WiFi Network Management

