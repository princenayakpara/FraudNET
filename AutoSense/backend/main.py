print("🔥 LOADED AUTOSENSE BACKEND:", __file__)
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import psutil
import time
import os
import winreg
import glob
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel
import uvicorn
import threading

from monitor import collect_metrics
from anomaly import AnomalyDetector
from health_score import calculate_health
from fix_engine import suggest_fixes, predict_degradation, auto_apply_fixes

# New Modules
import ai_engine
import deep_cleaner
import auto_mode
import security_monitor
import forecast_engine
import optimizer_engine
import auth
from auth import router as auth_router
import disk_analyzer
import apps_manager

app = FastAPI()
cpu_detector = AnomalyDetector()
ram_detector = AnomalyDetector()
last_records = []

app.include_router(auth_router)

# --- INSTANT CACHE SYSTEM ---
SCAN_CACHE = {
    "status": None,
    "junk": {"total_size_mb": 0, "files": [], "file_count": 0},
    "disk": {"folders": [], "treemap": {"children": []}, "top_files": [], "total_mb": 0},
    "security_ports": [],
    "network": {"upload_mbps": 0.0, "download_mbps": 0.0, "total_sent_mb": 0, "total_recv_mb": 0},
    "last_update": 0
}

def status_worker():
    """Independent thread for real-time metrics"""
    print("🚀 AutoSense Real-time Engine Started")
    global SCAN_CACHE
    
    # Init network tracking
    last_net_io = psutil.net_io_counters()
    last_net_time = time.time()

    while True:
        try:
            SCAN_CACHE["status"] = system_status_internal()
            
            # Network Calc
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - last_net_time
            if time_delta > 0:
                sent_bytes = current_net_io.bytes_sent - last_net_io.bytes_sent
                recv_bytes = current_net_io.bytes_recv - last_net_io.bytes_recv
                SCAN_CACHE["network"] = {
                    "upload_mbps": round((sent_bytes * 8) / (1024 * 1024) / time_delta, 2),
                    "download_mbps": round((recv_bytes * 8) / (1024 * 1024) / time_delta, 2),
                    "total_sent_mb": round(current_net_io.bytes_sent / (1024*1024), 2),
                    "total_recv_mb": round(current_net_io.bytes_recv / (1024*1024), 2)
                }
            last_net_io = current_net_io
            last_net_time = current_time
            time.sleep(2)
        except Exception as e:
            print(f"❌ Status Worker Error: {e}")
            time.sleep(2)

def heavy_scan_worker():
    """Independent thread for heavy IO tasks"""
    print("🚀 AutoSense Heavy Scan Engine Started")
    global SCAN_CACHE
    while True:
        try:
            now = time.time()
            if not SCAN_CACHE["disk"]["folders"] or (now - SCAN_CACHE["last_update"] > 600):
                print("♻️  Refreshing Heavy System Scans (Background)...")
                SCAN_CACHE["junk"] = deep_cleaner.scan_deep_junk()
                SCAN_CACHE["disk"] = disk_analyzer.analyze_user_home()
                SCAN_CACHE["security_ports"] = security_monitor.check_open_ports()
                SCAN_CACHE["last_update"] = now
                print("✅ Scans cached")
            time.sleep(10)
        except Exception as e:
            print(f"❌ Scan Worker Error: {e}")
            time.sleep(30)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=status_worker, daemon=True).start()
    threading.Thread(target=heavy_scan_worker, daemon=True).start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health-check")
def health_check():
    return {"message": "AutoSense backend running"}


@app.get("/status")
def system_status():
    if not SCAN_CACHE["status"]:
        return system_status_internal()
    return SCAN_CACHE["status"]

def system_status_internal():
    metrics = collect_metrics()

    cpu = round(float(metrics["cpu"]), 1)
    ram = round(float(metrics["ram"]), 1)
    disk = round(float(metrics["disk"]), 1)

    cpu_detector.update_history(cpu)
    ram_detector.update_history(ram)
    
    cpu_anomaly = cpu_detector.z_score_anomaly(cpu) or cpu_detector.isolation_forest_anomaly(cpu)
    ram_anomaly = ram_detector.z_score_anomaly(ram) or ram_detector.isolation_forest_anomaly(ram)
    
    anomaly = cpu_anomaly or ram_anomaly

    health = calculate_health(cpu, ram, disk, anomaly)
    fixes = suggest_fixes(cpu, ram, disk)

    record = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "health_score": health,
        "health_status": "CRITICAL" if anomaly else "NORMAL"
    }

    last_records.append(record)
    if len(last_records) > 10:
        last_records.pop(0)

    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "health_score": health,
        "health_status": record["health_status"],
        "fixes": fixes
    }

@app.get("/api/last-records")
def get_last_records():
    return last_records[::-1]

# 🔥 CPU Task Manager
@app.get("/api/top-cpu-processes")
def top_cpu_processes():
    psutil.cpu_percent(interval=0.5)

    procs = []
    for p in psutil.process_iter(['name', 'pid']):
        try:
            cpu = p.cpu_percent(interval=None)
            if cpu > 1:
                procs.append({
                    "name": p.info['name'],
                    "pid": p.info['pid'],
                    "cpu": round(cpu, 1)
                })
        except:
            pass

    return sorted(procs, key=lambda x: x["cpu"], reverse=True)[:8]

# 🧠 RAM Task Manager
@app.get("/api/top-memory-processes")
def top_memory_processes():
    procs = []
    for p in psutil.process_iter(['name','memory_info', 'pid']):
        try:
            mem = p.info['memory_info'].rss / (1024*1024)
            if mem > 30:
                procs.append({
                    "name": p.info['name'], 
                    "memory": round(mem, 2),
                    "pid": p.info['pid']
                })
        except:
            pass

    return sorted(procs, key=lambda x: x["memory"], reverse=True)[:8]

# 💾 Disk Task Manager
@app.get("/api/top-disk-processes")
def top_disk_processes():
    procs = []
    for p in psutil.process_iter(['name', 'pid']):
        try:
            io = p.io_counters()
            if io:
                read_bytes = io.read_bytes / (1024*1024)
                write_bytes = io.write_bytes / (1024*1024)
                total = read_bytes + write_bytes
                if total > 10:  # Only show processes with >10MB I/O
                    procs.append({
                        "name": p.info['name'],
                        "pid": p.info['pid'],
                        "read_mb": round(read_bytes, 2),
                        "write_mb": round(write_bytes, 2),
                        "total_mb": round(total, 2)
                    })
        except:
            pass
    
    return sorted(procs, key=lambda x: x["total_mb"], reverse=True)[:8]

# 💻 System Specs
@app.get("/api/system-specs")
def get_system_specs():
    import platform
    try:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "python_version": platform.python_version()
        }
    except:
        return {"error": "Failed to fetch specs"}

@app.get("/api/network-stats")
def get_network_stats():
    return SCAN_CACHE["network"]

# ========== NEW FEATURES ==========

# 🚀 One-Click Boost - Free RAM
@app.post("/api/boost-ram")
def boost_ram(token: str = Header(None)):
    """Terminate non-critical background processes to free RAM (Auth Required)"""
    auth.get_current_user(token)
    # List of safe-to-kill process names (non-critical)
    safe_to_kill = [
        "chrome.exe", "firefox.exe", "edge.exe", "opera.exe",
        "discord.exe", "spotify.exe", "steam.exe", "epicgameslauncher.exe",
        "skype.exe", "teams.exe", "zoom.exe", "slack.exe"
    ]
    
    freed_mb = 0
    killed_processes = []
    
    for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
        try:
            proc_name = proc.info['name'].lower()
            if any(safe in proc_name for safe in safe_to_kill):
                mem_mb = proc.info['memory_info'].rss / (1024*1024)
                proc.terminate()
                freed_mb += mem_mb
                killed_processes.append({
                    "name": proc.info['name'],
                    "pid": proc.info['pid'],
                    "freed_mb": round(mem_mb, 2)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return {
        "success": True,
        "freed_mb": round(freed_mb, 2),
        "killed_count": len(killed_processes),
        "processes": killed_processes
    }

# 🎯 Startup App Manager (Consolidated)
@app.get("/api/startup-apps")
def get_startup_apps_endpoint():
    """Get all Windows startup applications"""
    return apps_manager.get_startup_apps()

@app.post("/api/startup-apps/{app_name}/toggle")
def toggle_startup_app_endpoint(app_name: str, enabled: bool):
    """Enable or disable a startup application (Auth Removed for demo)"""
    return apps_manager.toggle_startup(app_name, enabled)

# 🧨 Force Remove App
@app.post("/api/apps/{app_name}/force")
def force_remove_app_endpoint(app_name: str):
    """Force remove app: Uninstall + Auto-Clean Leftovers"""
    return apps_manager.force_uninstall(app_name)

# 🗑️ Junk File Cleaner
@app.get("/api/junk-files/scan")
def scan_junk_files():
    """Scan for temporary and cache files"""
    junk_locations = [
        os.path.join(os.environ.get('TEMP', ''), '*'),
        os.path.join(os.environ.get('TMP', ''), '*'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp', '*'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'INetCache', '*'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Temporary Internet Files', '*'),
    ]
    
    junk_files = []
    total_size = 0
    
    for pattern in junk_locations:
        try:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        total_size += size
                        junk_files.append({
                            "path": file_path,
                            "size_mb": round(size / (1024*1024), 2),
                            "type": "temp" if "Temp" in file_path else "cache"
                        })
                except:
                    continue
        except:
            continue
    
    return {
        "total_files": len(junk_files),
        "total_size_mb": round(total_size / (1024*1024), 2),
        "files": sorted(junk_files, key=lambda x: x["size_mb"], reverse=True)[:100]  # Top 100
    }

@app.post("/api/junk-files/clean")
def clean_junk_files():
    """Delete temporary and cache files"""
    cleaned = 0
    freed_mb = 0
    errors = []
    
    # Clean temp directories
    temp_dirs = [
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
    ]
    
    for temp_dir in temp_dirs:
        if not os.path.exists(temp_dir):
            continue
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleaned += 1
                        freed_mb += size / (1024*1024)
                    except:
                        errors.append(file_path)
        except:
            continue
    
    return {
        "success": True,
        "cleaned_files": cleaned,
        "freed_mb": round(freed_mb, 2),
        "errors": len(errors)
    }

# 🔥 Advanced Task Manager - Enhanced with Kill
@app.get("/api/processes")
def get_all_processes():
    """Get all processes with CPU, RAM, and Disk usage"""
    processes = []
    
    for proc in psutil.process_iter(['name', 'pid', 'memory_info', 'cpu_percent']):
        try:
            proc.cpu_percent(interval=None)  # Warm up
        except:
            pass
    
    time.sleep(0.1)  # Small delay for CPU calculation
    
    for proc in psutil.process_iter(['name', 'pid', 'memory_info']):
        try:
            cpu = proc.cpu_percent(interval=None)
            mem_mb = proc.info['memory_info'].rss / (1024*1024)
            
            # Get I/O stats
            io_mb = 0
            try:
                io = proc.io_counters()
                if io:
                    io_mb = (io.read_bytes + io.write_bytes) / (1024*1024)
            except:
                pass
            
            processes.append({
                "name": proc.info['name'],
                "pid": proc.info['pid'],
                "cpu": round(cpu, 1),
                "memory_mb": round(mem_mb, 2),
                "disk_io_mb": round(io_mb, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return sorted(processes, key=lambda x: x["cpu"] + x["memory_mb"], reverse=True)[:50]

@app.post("/api/processes/{pid}/kill")
def kill_process(pid: int):
    """Kill a process by PID (Auth Removed)"""
    # auth.get_current_user(token) 
    return apps_manager.kill_process(pid)
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return {"success": True, "message": f"Process {pid} terminated"}
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Process not found")
    except psutil.AccessDenied:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🤖 AI Optimization Engine
@app.get("/api/ai/predict")
def ai_predict():
    """Predict performance degradation"""
    metrics = collect_metrics()
    cpu = round(float(metrics["cpu"]), 1)
    ram = round(float(metrics["ram"]), 1)
    disk = round(float(metrics["disk"]), 1)
    
    # Use the new AI Engine for advanced prediction
    prediction = ai_engine.analyze_system(cpu, ram, disk)
    return prediction

class ChatMessage(BaseModel):
    message: str

@app.post("/api/ai/chat")
def ai_chat(chat: ChatMessage):
    """Chat with AutoSense AI"""
    return {"response": ai_engine.chat_with_bot(chat.message)}

@app.post("/api/ai/auto-optimize")
def ai_auto_optimize(token: str = Header(None)):
    """Auto-apply AI-suggested optimizations (Auth Required)"""
    auth.get_current_user(token)
    metrics = collect_metrics()
    cpu = round(float(metrics["cpu"]), 1)
    ram = round(float(metrics["ram"]), 1)
    disk = round(float(metrics["disk"]), 1)
    
    result = auto_apply_fixes(cpu, ram, disk)
    return result

# ==========================================
# 🧹 1️⃣ Deep Cleaner Engine
# ==========================================
@app.get("/api/deep-clean/scan")
def api_deep_clean_scan():
    return SCAN_CACHE["junk"]

@app.post("/api/deep-clean/clean")
def api_deep_clean_clean(token: str = Header(None)):
    auth.get_current_user(token)
    try:
        res = deep_cleaner.clean_deep_junk()
        # Trigger immediate background re-scan to update cache
        SCAN_CACHE["junk"] = {"total_size_mb": 0, "files": [], "file_count": 0}
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

# ==========================================
# 📂 4️⃣ Disk Space Analyzer (WizTree Edition)
# ==========================================
@app.get("/api/disk/scan")
def api_disk_scan():
    """Returns the latest cached disk scan (instantly)"""
    return SCAN_CACHE["disk"]

@app.delete("/api/disk/file")
def api_delete_file(path: str, token: str = Header(None)):
    """Delete a specific file (Auth Required)"""
    auth.get_current_user(token)
    try:
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
            return {"success": True, "message": "File deleted"}
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# ⚡ 2️⃣ Auto Performance Mode
# ==========================================
@app.post("/api/ai/auto-mode/start")
def api_auto_mode_start():
    success = auto_mode.start_auto_mode()
    return {"success": success, "status": "running" if success else "already_running"}

@app.post("/api/ai/auto-mode/stop")
def api_auto_mode_stop():
    success = auto_mode.stop_auto_mode()
    return {"success": success, "status": "stopped" if success else "not_running"}

# ==========================================
# 🔐 3️⃣ Device Security Monitor
# ==========================================
@app.get("/api/security/firewall-status")
def api_firewall_status():
    status = security_monitor.check_firewall_status()
    return {"enabled": status}

@app.post("/api/security/enable-firewall")
def api_enable_firewall():
    success = security_monitor.enable_firewall()
    return {"success": success}

@app.get("/api/security/open-ports")
def api_open_ports():
    return SCAN_CACHE["security_ports"]

# ==========================================
# 📊 4️⃣ AI Health Forecast Engine
# ==========================================
@app.get("/api/ai/forecast")
def api_ai_forecast():
    metrics = collect_metrics()
    cpu = round(float(metrics["cpu"]), 1)
    ram = round(float(metrics["ram"]), 1)
    disk = round(float(metrics["disk"]), 1)
    return forecast_engine.predict_health(cpu, ram, disk)

# ==========================================
# 🧠 5️⃣ Smart Resource Optimizer
# ==========================================
@app.post("/api/ai/optimize-now")
def api_optimize_now():
    return optimizer_engine.optimize_system()


# --------------------------
# 🚀 AUTOSENSE X - NEW API MODULES
# --------------------------

# 1️⃣ AI SYSTEM BRAIN
@app.get("/api/ai/predict")
def api_ai_predict():
    """Real-time AI Prediction of System Failure Risk"""
    metrics = collect_metrics()
    cpu = round(float(metrics["cpu"]), 1)
    ram = round(float(metrics["ram"]), 1)
    disk = round(float(metrics["disk"]), 1)
    return ai_engine.analyze_system(cpu, ram, disk)

# 3️⃣ WIZTREE DISK MAP
@app.get("/api/disk-map")
def api_disk_map():
    """Returns the Treemap JSON for D3.js visualization"""
    if SCAN_CACHE["disk"]:
        # Ensure we return the treemap structure
        return SCAN_CACHE["disk"].get("treemap", {"children": []})
    return {"name": "Scanning...", "children": []}

# 5️⃣ SECURITY CENTER - MALWARE SUSPICION
@app.get("/api/security/scan")
def api_security_scan():
    """Heuristic Malware Scan (Simulated for Demo)"""
    # Use existing open ports as a base for suspicion
    ports = SCAN_CACHE["security_ports"]
    suspicious_count = len([p for p in ports if p.get("risk") == "HIGH"])
    
    status = "CLEAN"
    if suspicious_count > 0: status = "AT_RISK"
    
    return {
        "status": status,
        "risk_level": "HIGH" if suspicious_count > 0 else "LOW",
        "suspicious_pids": [], # Placeholder for future expansion
        "active_threats": suspicious_count,
        "message": f"Scan complete. Found {suspicious_count} potential security risks."
    }

# --------------------------
# APPS MANAGER API
# --------------------------
@app.get("/api/apps/processes")
def get_processes():
    return apps_manager.get_running_processes()

@app.post("/api/apps/kill")
def kill_app_process(pid: int):
    return apps_manager.kill_process(pid)

@app.get("/api/apps/startup")
def get_startup():
    return apps_manager.get_startup_apps()

# --- REVO UNINSTALLER API ---
@app.get("/api/apps/installed")
def get_installed():
    return apps_manager.get_installed_apps()

class UninstallRequest(BaseModel):
    command: str

@app.post("/api/apps/uninstall")
def run_uninstaller(req: UninstallRequest):
    # auth.get_current_user(token) # Removed for local usage convenience
    return apps_manager.uninstall_app(req.command)

@app.get("/api/apps/leftovers")
def scan_app_leftovers(app_name: str):
    return apps_manager.scan_leftovers(app_name)

@app.delete("/api/apps/leftovers")
def delete_app_leftover(path: str):
    # auth.get_current_user(token) # Removed for local usage convenience
    return apps_manager.delete_leftover(path)

# --------------------------
# LARGE FILES API
# --------------------------
@app.get("/api/disk/partitions")
def get_partitions():
    return deep_cleaner.get_partitions()

@app.get("/api/large-files")
def get_large_files(path: str = None):
    return deep_cleaner.scan_large_files(path=path)

@app.post("/api/large-files/delete")
def delete_large_file(path: str):
    # auth.get_current_user(token) # Removed global auth
    return deep_cleaner.delete_large_file(path)


# Mount Frontend (Must be last to avoid overriding API routes)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

print(f"📂 Mount Path: {FRONTEND_DIR}")
print(f"📄 CSS Path: {FRONTEND_DIR / 'style.css'}")
print(f"📄 CSS Exists: {(FRONTEND_DIR / 'style.css').exists()}")

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    print("🚀 Starting AutoSense Server on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
