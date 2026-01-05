# Fix PyQt6 DLL Error

## The Problem
```
ImportError: DLL load failed while importing QtCore: The specified procedure could not be found.
```

This error occurs because PyQt6 requires Visual C++ Redistributables on Windows.

## Solution 1: Install Visual C++ Redistributables (Recommended)

1. Download and install **Microsoft Visual C++ Redistributable**:
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Or search for "Visual C++ Redistributable 2015-2022"

2. After installing, restart your computer

3. Try running again:
```bash
python main.py
```

## Solution 2: Use Web Frontend (No PyQt6 Required)

Since PyQt6 has DLL issues, use the web-based frontend instead:

1. **Start the API server:**
```bash
python app.py
```

2. **In another terminal, start the web frontend:**
```bash
python run_web_frontend.py
```

3. **Browser will open automatically** at `http://localhost:8080`

The web frontend has all the same features:
- Network scanning
- Connect to networks
- View logs
- Train model
- Export data

## Solution 3: Use PyQt5 Instead

If you prefer desktop app, try PyQt5 (more stable on Windows):

```bash
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PyQt5
```

Then modify `main.py` to use PyQt5:
- Change `from PyQt6` to `from PyQt5`
- Change `QApplication` import accordingly

## Solution 4: Use Virtual Environment

Sometimes the issue is with the Python installation. Try a fresh virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Recommended: Use Web Frontend

The web frontend is the easiest solution and doesn't require any DLLs. Just run:

```bash
# Terminal 1: Start API
python app.py

# Terminal 2: Start Web UI
python run_web_frontend.py
```

Then open your browser to `http://localhost:8080`

