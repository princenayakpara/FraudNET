import os
import time
from typing import List, Dict

# Category Mapping
CATEGORIES = {
    'Media': ['.mp4', '.mkv', '.mov', '.avi', '.mp3', '.wav', '.flac', '.png', '.jpg', '.jpeg', '.gif', '.svg'],
    'Documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md'],
    'System/Dev': ['.exe', '.dll', '.sys', '.py', '.js', '.html', '.css', '.json', '.cpp', '.h', '.java', '.cs'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
}

def get_folder_size(path: str) -> Dict:
    """Recursively scan a folder using os.scandir for top performance"""
    total_size = 0
    file_count = 0
    cat_distribution = {cat: 0 for cat in CATEGORIES}
    cat_distribution['Others'] = 0
    large_files = []

    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        size = entry.stat().st_size
                        total_size += size
                        file_count += 1
                        
                        # Category detection
                        _, ext = os.path.splitext(entry.name)
                        ext = ext.lower()
                        found_cat = False
                        for cat, extensions in CATEGORIES.items():
                            if ext in extensions:
                                cat_distribution[cat] += size
                                found_cat = True
                                break
                        if not found_cat:
                            cat_distribution['Others'] += size
                            
                        # Track large files (> 50MB)
                        if size > 50 * 1024 * 1024:
                            large_files.append({
                                "name": entry.name,
                                "path": entry.path,
                                "size_mb": round(size / (1024*1024), 2)
                            })
                    elif entry.is_dir(follow_symlinks=False):
                        # Recursive call
                        sub_res = get_folder_size(entry.path)
                        total_size += sub_res['total_size_bytes']
                        file_count += sub_res['file_count']
                        for cat in cat_distribution:
                            cat_distribution[cat] += sub_res['cat_distribution'].get(cat, 0)
                        large_files.extend(sub_res['large_files'])
                except Exception:
                    continue
    except PermissionError:
        pass # Skip folders we can't access
        
    return {
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024*1024), 2),
        "file_count": file_count,
        "cat_distribution": {k: round(v / (1024*1024), 2) for k, v in cat_distribution.items()},
        "large_files": sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:50]
    }

def analyze_user_home() -> Dict:
    """Analyze the user's home directory (Documents, Downloads, etc.)"""
    home = os.path.expanduser("~")
    target_dirs = ["Downloads", "Documents", "Desktop", "Videos", "Music", "Pictures"]
    
    start_time = time.time()
    results = []
    
    for d in target_dirs:
        path = os.path.join(home, d)
        if os.path.exists(path):
            res = get_folder_size(path)
            res["folder_name"] = d
            results.append(res)
            
    # Aggregated
    total_mb = sum(r['total_size_mb'] for r in results)
    total_files = sum(r['file_count'] for r in results)
    
    # Calculate global category sum
    global_cats = {cat: 0 for cat in CATEGORIES}
    global_cats['Others'] = 0
    all_large_files = []
    
    for r in results:
        for cat, val in r['cat_distribution'].items():
            global_cats[cat] += val
        all_large_files.extend(r['large_files'])
        
    return {
        "scanning_time": round(time.time() - start_time, 2),
        "total_mb": round(total_mb, 2),
        "total_files": total_files,
        "folders": sorted(results, key=lambda x: x['total_size_mb'], reverse=True),
        "distribution": global_cats,
        "top_files": sorted(all_large_files, key=lambda x: x['size_mb'], reverse=True)[:100],
        "treemap": {
            "name": "AutoSense Search",
            "children": [
                {
                    "name": r["folder_name"],
                    "value": r["total_size_mb"],
                    "children": [
                        {"name": f["name"], "value": f["size_mb"]} for f in r["large_files"]
                    ]
                } for r in results if r["total_size_mb"] > 0
            ]
        }
    }
