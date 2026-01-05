import psutil
import winreg
import subprocess

# --- PROCESS MANAGER ---
def get_running_processes():
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
        try:
            # Trigger cpu_percent
            p.cpu_percent(interval=None)
            procs.append(p)
        except: pass
    
    # Sort by Memory usage
    procs.sort(key=lambda p: p.info['memory_info'].rss, reverse=True)
    
    result = []
    for p in procs[:50]: # Top 50
        try:
            io = p.io_counters()
            io_mb = (io.read_bytes + io.write_bytes) / (1024*1024)
        except: io_mb = 0
            
        result.append({
            "pid": p.info['pid'],
            "name": p.info['name'],
            "cpu": round(p.cpu_percent(interval=None), 1),
            "ram_mb": round(p.info['memory_info'].rss / (1024*1024), 1),
            "disk_io_mb": round(io_mb, 2)
        })
    return result

def kill_process(pid: int):
    try:
        p = psutil.Process(pid)
        p.terminate()
        return {"success": True, "message": f"Process {pid} terminated"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# --- STARTUP MANAGER ---
def get_startup_apps():
    apps = []
    locations = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run")
    ]
    
    for hkey, path in locations:
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(key, i)
                        apps.append({
                            "name": name,
                            "command": val,
                            "location": "HKCU" if hkey == winreg.HKEY_CURRENT_USER else "HKLM",
                            "enabled": True,
                            "can_toggle": hkey == winreg.HKEY_CURRENT_USER # HKLM requires admin
                        })
                        i += 1
                    except OSError: break
        except: pass
    return apps

def toggle_startup(app_name: str, enable: bool):
    """
    Toggles startup status. 
    Note: Real disabling usually involves moving values to a 'StartupApproved' key or deleting them.
    For this implementation, 'Disable' will DELETE the key from HKCU Run.
    Re-enabling is hard without storing the command commands.
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        if not enable:
            # DISABLE -> Search and Delete from HKCU
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, app_name)
                    return {"success": True, "message": f"Disabled {app_name} (Removed from HKCU)"}
            except FileNotFoundError:
                return {"success": False, "message": "App not found in HKCU Startup items."}
        else:
            return {"success": False, "message": "Re-enabling requires manual addition in this version."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def force_uninstall(app_name: str):
    """
    Simulates a 'Force Remove' by:
    1. Finding the uninstaller string
    2. Attempting a quiet uninstall if possible (heuristic)
    3. Scanning for and deleting leftovers immediately
    """
    # 1. Get Uninstaller
    target_app = None
    all_apps = get_installed_apps()
    for app in all_apps:
        if app['name'].lower() == app_name.lower():
            target_app = app
            break
    
    log = []
    
    if target_app:
        uninstall_cmd = target_app.get("uninstall_string", "")
        if uninstall_cmd:
            # Try to force quiet
            if "msiexec" in uninstall_cmd.lower():
                uninstall_cmd = uninstall_cmd.replace("/I", "/x") + " /quiet /norestart"
            
            log.append(f"Launching Uninstaller: {uninstall_cmd}")
            subprocess.Popen(uninstall_cmd, shell=True)
    else:
        log.append("App entry not found in registry, proceeding to leftover scan...")

    # 2. Leftover Scan & Delete
    leftovers = scan_leftovers(app_name)
    deleted_count = 0
    freed_mb = 0
    
    for item in leftovers:
        res = delete_leftover(item['path'])
        if res.get("success"):
            deleted_count += 1
            freed_mb += item.get("size_mb", 0)
            log.append(f"Deleted: {item['path']}")
    
    return {
        "success": True,
        "message": "Force removal process initiated.",
        "log": log,
        "leftovers_removed": deleted_count,
        "freed_mb": round(freed_mb, 2)
    }

# --- UNINSTALLER MANAGER (REVO STYLE) ---
def get_installed_apps():
    """Scan Registry for installed programs"""
    apps = []
    # Registry keys where uninstallers are listed
    keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hkey, path in keys:
        try:
            with winreg.OpenKey(hkey, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            try:
                                name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                uninstall_string = winreg.QueryValueEx(sub_key, "UninstallString")[0]
                                
                                # Optional fields
                                try: icon = winreg.QueryValueEx(sub_key, "DisplayIcon")[0]
                                except: icon = ""
                                try: version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                                except: version = ""
                                
                                apps.append({
                                    "id": sub_key_name,
                                    "name": name,
                                    "version": version,
                                    "uninstall_string": uninstall_string,
                                    "icon": icon
                                })
                            except FileNotFoundError:
                                pass # Missing DisplayName or UninstallString
                    except OSError:
                        pass
        except OSError:
            pass
            
    # Dedup by name
    unique_apps = {app['name']: app for app in apps}.values()
    return sorted(list(unique_apps), key=lambda x: x['name'])

def uninstall_app(uninstall_string):
    """Launch the uninstaller"""
    try:
        # Some strings are like 'MsiExec.exe /I{...}' or '"C:\Program Files\..." /uninstall'
        # We use 'start' in cmd to ensure it launches as a separate window/process and handles some UAC prompts.
        # But simplistic shell=True is usually enough. 
        # CAUTION: 'start' command in Windows cmd expects a title if the first arg is quoted.
        # So we use: start "" "command"
        
        full_cmd = f'start "" {uninstall_string}'
        subprocess.Popen(full_cmd, shell=True)
        return {"success": True, "message": "Uninstaller launched"}
    except Exception as e:
        return {"success": False, "message": str(e)}

import os
import shutil

def scan_leftovers(app_name):
    """Scan for probable leftovers in AppData"""
    leftovers = []
    
    # Common paths to search
    search_paths = [
        os.path.join(os.environ['APPDATA']),          # Roaming
        os.path.join(os.environ['LOCALAPPDATA']),     # Local
        os.environ.get('ProgramFiles', 'C:\\Program Files'),
        os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    ]
    
    # Simple heuristic: Look for folder exactly matching app name (case insensitive)
    # or starting with app name (risky, so we stick to exact or very close matches)
    
    # Cleaning name for search (remove version numbers, 'Inc', etc if needed)
    # For safety, let's strict match the first word if it's unique enough, or the full name.
    # Let's try exact match of the folder name against the App Name.
    
    search_term = app_name.lower().replace(" ", "")
    
    for base_path in search_paths:
        if not os.path.exists(base_path): continue
        
        try:
            for item in os.listdir(base_path):
                # Check if item name is similar to app name
                item_clean = item.lower().replace(" ", "")
                if search_term in item_clean and len(item_clean) > 3: 
                    # MATCH FOUND
                    full_path = os.path.join(base_path, item)
                    if os.path.isdir(full_path):
                        size = 0
                        for r, d, f in os.walk(full_path):
                            for file in f:
                                size += os.path.getsize(os.path.join(r, file))
                        
                        leftovers.append({
                            "path": full_path,
                            "type": "folder",
                            "size_mb": round(size / (1024*1024), 2)
                        })
        except: pass
        
    return leftovers

def delete_leftover(path):
    if not os.path.exists(path): return {"success": False, "message": "Path not found"}
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {"success": True, "message": "Deleted"}
    except Exception as e:
        return {"success": False, "message": str(e)}
