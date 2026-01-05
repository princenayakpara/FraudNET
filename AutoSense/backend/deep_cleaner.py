import os
import glob
import shutil
from typing import List, Dict

# Common Windows Junk Paths
JUNK_PATTERNS = [
    os.path.join(os.environ.get('TEMP', ''), '*'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp', '*'),
    os.path.join(os.environ.get('WINDIR', ''), 'Temp', '*'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'INetCache', '*'),  # IE/Edge Cache
    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache', '*'), # Chrome Cache
]

import time

_cache = {
    "junk_data": None,
    "last_scan": 0
}

def scan_deep_junk() -> Dict:
    global _cache
    if _cache["junk_data"] and (time.time() - _cache["last_scan"] < 600):
        return _cache["junk_data"]
        
    junk_files = []
    total_size = 0
    
    for pattern in JUNK_PATTERNS:
        try:
            files = glob.glob(pattern)
            for f in files:
                try:
                    if os.path.isfile(f):
                        size = os.path.getsize(f)
                        total_size += size
                        junk_files.append({
                            "path": f,
                            "size_mb": round(size / (1024*1024), 2),
                            "name": os.path.basename(f)
                        })
                except: pass
        except: pass
        
    res = {
        "file_count": len(junk_files),
        "total_size_mb": round(total_size / (1024*1024), 2),
        "files": junk_files[:100]  # Return top 100 for display
    }
    _cache["junk_data"] = res
    _cache["last_scan"] = time.time()
    return res

def clean_deep_junk() -> Dict:
    global _cache
    _cache["junk_data"] = None  # Force re-scan next time
    deleted_count = 0
    freed_bytes = 0
    errors = []
    
    for pattern in JUNK_PATTERNS:
        try:
            files = glob.glob(pattern)
            for f in files:
                try:
                    if os.path.isfile(f):
                        size = os.path.getsize(f)
                        os.remove(f)
                        freed_bytes += size
                        deleted_count += 1
                    elif os.path.isdir(f):
                         # Be careful with directories, only empty ones or specific temp dirs
                         shutil.rmtree(f, ignore_errors=True)
                except Exception as e:
                    errors.append(str(e))
        except: pass

    return {
        "success": True,
        "deleted_count": deleted_count,
        "freed_mb": round(freed_bytes / (1024*1024), 2),
        "errors_count": len(errors)
    }

import psutil

def get_partitions():
    partitions = []
    try:
        for part in psutil.disk_partitions():
            if 'cdrom' in part.opts or part.fstype == '': continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except: pass
    except: pass
    return partitions

def scan_large_files(limit_mb=100, path=None) -> List[Dict]:
    """Scan directory for large files > limit_mb"""
    large_files = []
    
    # If path is provided, scan that drive/folder. 
    # Otherwise scan User Home.
    if path:
         scan_dirs = [path]
    else:
        home = os.path.expanduser("~")
        scan_dirs = [
            os.path.join(home, "Downloads"),
            os.path.join(home, "Documents"),
            os.path.join(home, "Videos"),
            os.path.join(home, "Desktop")
        ]

    for d in scan_dirs:
        try:
            for root, _, files in os.walk(d):
                for name in files:
                    try:
                        filepath = os.path.join(root, name)
                        size = os.path.getsize(filepath)
                        if size > limit_mb * 1024 * 1024:
                            large_files.append({
                                "path": filepath,
                                "name": name,
                                "size_mb": round(size / (1024*1024), 2)
                            })
                    except: pass
        except: pass
    
    return sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:50]

def delete_large_file(path: str):
    if os.path.exists(path) and os.path.isfile(path):
        os.remove(path)
        return {"success": True}
    return {"success": False, "error": "File not found"}
