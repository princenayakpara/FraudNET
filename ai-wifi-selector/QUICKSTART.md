# Quick Start Guide

## Installation

1. **Install Python 3.10+** (if not already installed)

2. **Install Dependencies:**
```bash
cd ai-wifi-selector
pip install -r requirements.txt
```

3. **Run the Application:**
```bash
# GUI Mode (Recommended)
python main.py

# API Mode (Headless)
python app.py
```

## First Run

1. The application will check for WiFi adapter
2. If no ML model exists, it will train an initial model (requires some network logs first)
3. Dashboard will open showing available networks
4. Click "Scan Networks" to refresh the list
5. Click "Connect to Best" to use ML prediction

## Building Executable

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build executable
pyinstaller --onefile --noconsole --name "AI-WiFi-Selector" main.py

# Or use the spec file
pyinstaller AI-WiFi-Selector.spec
```

The executable will be in the `dist/` folder.

## API Usage

Start the application, then access the API at `http://127.0.0.1:8000`

Example API calls:

```bash
# Get status
curl http://127.0.0.1:8000/api/status

# Get networks
curl http://127.0.0.1:8000/api/networks

# Connect to best network
curl -X POST http://127.0.0.1:8000/api/best

# Switch to specific network
curl -X POST http://127.0.0.1:8000/api/switch -H "Content-Type: application/json" -d '{"ssid": "MyNetwork"}'
```

## Troubleshooting

### No WiFi Adapter Error
- Ensure WiFi adapter is enabled
- Run as Administrator if needed
- Check Windows WiFi settings

### Model Training Fails
- Need at least 10 network log entries
- Connect to different networks to generate logs
- Manually trigger training from dashboard

### Connection Fails
- Check if network requires password
- Ensure network is in range
- Try manual connection first

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

## Features Overview

- **Auto-Switching**: Automatically switches when connection degrades
- **ML Prediction**: Uses RandomForest to predict best network
- **Background Monitoring**: Runs in background, checks every 60 seconds
- **System Tray**: Minimize to tray, right-click to show/quit
- **Notifications**: Desktop notifications on network switches
- **Logging**: All metrics stored in SQLite database
- **Export**: Export logs to CSV/JSON from dashboard

## Configuration

- Monitoring interval: 60 seconds (in `core/monitor.py`)
- Training interval: 24 hours (in `app.py`)
- Log retention: 30 days (in `app.py`)

