# How to View the Frontend

## Option 1: PyQt6 Desktop GUI (Main Frontend)

The main frontend is a **PyQt6 desktop application** with a modern dashboard.

### Steps:

1. **Navigate to project directory:**
```bash
cd E:\Fraudnet\FraudNET\FraudNET\ai-wifi-selector
```

2. **Install dependencies (if not already done):**
```bash
pip install -r requirements.txt
```

3. **Run the GUI application:**
```bash
python main.py
```

### What You'll See:

- **Dashboard Window** with:
  - **Networks Tab**: List of all available WiFi networks with signal strength, RSSI, security, ML score, and Connect buttons
  - **Logs Tab**: Historical network logs with metrics (download, upload, ping, packet loss, scores)
  - **Settings Tab**: Monitoring controls and model information

- **Status Bar**: Shows current connection status
- **Action Buttons**: 
  - Scan Networks
  - Connect to Best (uses ML prediction)
  - Train Model
  - Export Logs

- **System Tray Icon**: App minimizes to system tray (right-click to show/quit)

## Option 2: REST API (Browser/Postman)

The application also runs a FastAPI server that you can access via browser or API client.

### Steps:

1. **Start the application** (either mode):
```bash
python main.py  # GUI mode (includes API)
# OR
python app.py  # API-only mode
```

2. **Open browser and visit:**
```
http://127.0.0.1:8000
```

3. **API Endpoints:**
- `http://127.0.0.1:8000/api/status` - Application status
- `http://127.0.0.1:8000/api/networks` - Available networks (JSON)
- `http://127.0.0.1:8000/api/logs` - Network logs (JSON)
- `http://127.0.0.1:8000/api/current` - Current connection

### Interactive API Docs:

Visit `http://127.0.0.1:8000/docs` for Swagger UI (interactive API documentation)

## Troubleshooting

### If GUI doesn't open:
- Check if PyQt6 is installed: `pip install PyQt6`
- Check for errors in console
- Ensure Python 3.10+ is being used

### If no networks show:
- Click "Scan Networks" button
- Check WiFi adapter is enabled
- Run as Administrator if needed

### If API doesn't respond:
- Check if port 8000 is available
- Look for errors in console
- Verify FastAPI is installed: `pip install fastapi uvicorn`

## Quick Test

```bash
# Terminal 1: Start the app
cd E:\Fraudnet\FraudNET\FraudNET\ai-wifi-selector
python main.py

# Terminal 2: Test API (optional)
curl http://127.0.0.1:8000/api/status
```

The dashboard window should appear automatically when you run `main.py`!

