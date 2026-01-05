# AutoSense PC Manager - Architecture & User Flow

## Overview
AutoSense PC Manager is an upgraded version of AutoSense that adds PC management features inspired by Microsoft PC Manager. It maintains all existing monitoring capabilities while adding new optimization tools.

## Architecture

### Backend (FastAPI)
**File: `backend/main.py`**

#### Existing Endpoints (Preserved)
- `GET /` - Health check
- `GET /status` - System metrics (CPU, RAM, Disk) with health score
- `GET /api/last-records` - Last 10 monitoring records
- `GET /api/top-cpu-processes` - Top CPU consuming processes (enhanced with PID)
- `GET /api/top-memory-processes` - Top RAM consuming processes (enhanced with PID)

#### New Endpoints

**1. One-Click Boost**
- `POST /api/boost-ram` - Frees RAM by terminating non-critical processes
  - Returns: freed MB, killed process count, list of terminated processes
  - Safe process list: Chrome, Firefox, Edge, Discord, Spotify, Steam, etc.

**2. Startup App Manager**
- `GET /api/startup-apps` - Lists all Windows startup applications
  - Scans HKCU and HKLM registry paths
  - Returns: name, command, enabled status, location
- `POST /api/startup-apps/{app_name}/toggle` - Enable/disable startup app
  - Modifies Windows registry

**3. Junk File Cleaner**
- `GET /api/junk-files/scan` - Scans for temporary and cache files
  - Scans: TEMP, TMP, LocalAppData\Temp, Internet Cache
  - Returns: file count, total size, top 100 files
- `POST /api/junk-files/clean` - Deletes temporary files
  - Returns: cleaned file count, freed MB

**4. Advanced Task Manager**
- `GET /api/top-disk-processes` - Top disk I/O processes
  - Returns: process name, PID, read/write MB, total MB
- `GET /api/processes` - All processes with CPU, RAM, Disk I/O
  - Returns: top 50 processes sorted by resource usage
- `POST /api/processes/{pid}/kill` - Kill process by PID
  - Handles access denied and process not found errors

**5. AI Optimization Engine**
- `GET /api/ai/predict` - Predicts performance degradation
  - Analyzes CPU, RAM, Disk metrics
  - Returns: risk score (0-100), overall risk level, predictions per metric
  - Includes confidence scores and recommendations
- `POST /api/ai/auto-optimize` - Auto-applies optimizations
  - Conditionally applies: RAM boost (if RAM > 80%), junk cleanup (if Disk > 85%), high CPU kill (if CPU > 85%)
  - Returns: applied fixes and results

### Backend Modules

**`backend/fix_engine.py`** - Enhanced with:
- `predict_degradation()` - AI-powered risk assessment
- `auto_apply_fixes()` - Automatic optimization application
- Helper functions for RAM boost, junk cleanup, and process termination

### Frontend (Vanilla JavaScript)
**File: `frontend/script.js`**

#### Existing Features (Preserved)
- Real-time metrics display (CPU, RAM, Disk, Health)
- Chart.js visualization
- Historical records table
- Modal system for process viewing
- Theme toggle

#### New Features

**1. One-Click Boost UI**
- Button triggers RAM boost
- Shows freed MB and process count
- Auto-refreshes metrics after boost

**2. Startup Manager UI**
- Button opens modal with all startup apps
- Toggle buttons to enable/disable apps
- Shows app name, command, and location

**3. Junk File Cleaner UI**
- "Scan Files" button scans and displays results
- "Clean Now" button with confirmation dialog
- Shows file count and total size
- Modal displays top 100 files

**4. Advanced Task Manager UI**
- Button opens modal with all processes
- Shows CPU, RAM, Disk I/O for each process
- "Kill" button for each process with confirmation
- Real-time updates

**5. AI Optimization UI**
- "Predict Issues" button shows risk assessment
- Modal displays predictions with risk levels and confidence
- "Auto-Optimize" button with confirmation
- Shows applied fixes and results

### Frontend Styling
**File: `frontend/style.css`**

- New `.pc-manager-section` with grid layout
- `.manager-card` for feature cards
- `.action-btn` for primary/secondary buttons
- `.result-text` for status messages
- Enhanced modal styles for better content display

## User Flow

### 1. System Monitoring (Existing)
- User opens dashboard
- Real-time metrics update every 3 seconds
- Click CPU/RAM/Disk cards to view top processes
- View historical data in table
- Monitor health score and suggested fixes

### 2. One-Click Boost
1. User clicks "Boost Now" button
2. System terminates non-critical processes
3. Results show freed MB and process count
4. Metrics auto-refresh to show improved RAM usage

### 3. Startup Manager
1. User clicks "View Startup Apps"
2. Modal displays all startup applications
3. User can toggle enable/disable for each app
4. Changes are saved to Windows registry

### 4. Junk File Cleaner
1. User clicks "Scan Files"
2. System scans temp/cache directories
3. Results show file count and total size
4. Modal displays top 100 files
5. User clicks "Clean Now" to delete files
6. Confirmation dialog appears
7. Files are deleted and freed space is shown

### 5. Advanced Task Manager
1. User clicks "Open Task Manager"
2. Modal displays all processes with resource usage
3. User can click "Kill" button on any process
4. Confirmation dialog appears
5. Process is terminated and removed from list
6. Metrics auto-refresh

### 6. AI Optimization
1. User clicks "Predict Issues"
2. System analyzes current metrics
3. Modal shows risk score, predictions, and recommendations
4. User clicks "Auto-Optimize" to apply fixes
5. Confirmation dialog appears
6. System automatically applies optimizations
7. Results show what was fixed and metrics improve

## Technical Details

### Dependencies
- **Backend**: FastAPI, psutil, winreg (built-in), numpy, scikit-learn, pandas
- **Frontend**: Vanilla JavaScript, Chart.js (CDN)

### Security Considerations
- Process termination requires appropriate permissions
- Registry modifications are limited to startup apps
- File deletion is restricted to temp/cache directories
- Confirmation dialogs prevent accidental actions

### Error Handling
- All API calls have try-catch blocks
- HTTP exceptions for invalid requests
- Graceful degradation if features fail
- User-friendly error messages

### Performance
- Efficient process iteration with psutil
- Cached CPU calculations
- Limited result sets (top 50-100 items)
- Async/await for non-blocking operations

## Future Enhancements
- Scheduled auto-optimization
- Customizable safe-to-kill process list
- Startup app import/export
- Detailed optimization history
- Performance benchmarks

