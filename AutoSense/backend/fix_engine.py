import psutil
import os
import glob

def suggest_fixes(cpu, ram, disk):
    fixes = []

    if cpu > 85:
        fixes.append("Close high CPU background processes")
    if ram > 80:
        fixes.append("Free RAM or restart the system")
    if disk > 80:
        fixes.append("Disk usage is high. Clean unnecessary files")

    if not fixes:
        fixes.append("System healthy")

    return fixes

def predict_degradation(cpu, ram, disk, cpu_anomaly=False, ram_anomaly=False, disk_anomaly=False):
    """AI-powered prediction of performance degradation using Hybrid Analysis (Heuristic + ML)"""
    risk_score = 0
    predictions = []
    
    # CPU prediction
    if cpu > 90:
        risk_score += 40
        predictions.append({
            "metric": "CPU",
            "current": f"{cpu}%",
            "risk": "CRITICAL",
            "prediction": "System may freeze or become unresponsive within 5-10 minutes",
            "confidence": 0.95
        })
    elif cpu_anomaly: # ML Detected Anomaly even if usage is not peak
        risk_score += 35
        predictions.append({
            "metric": "CPU",
            "current": f"{cpu}%",
            "risk": "HIGH",
            "prediction": "Unusual CPU behavior detected by ML model. Malware or infinite loop suspected.",
            "confidence": 0.85
        })
    elif cpu > 75:
        risk_score += 25
        predictions.append({
            "metric": "CPU",
            "current": f"{cpu}%",
            "risk": "HIGH",
            "prediction": "Performance degradation expected in 15-30 minutes",
            "confidence": 0.80
        })
    elif cpu > 60:
        risk_score += 10
        predictions.append({
            "metric": "CPU",
            "current": f"{cpu}%",
            "risk": "MEDIUM",
            "prediction": "Minor slowdowns possible",
            "confidence": 0.60
        })
    
    # RAM prediction
    if ram > 90:
        risk_score += 40
        predictions.append({
            "metric": "RAM",
            "current": f"{ram}%",
            "risk": "CRITICAL",
            "prediction": "System may start swapping to disk, causing severe slowdowns",
            "confidence": 0.90
        })
    elif ram_anomaly:
        risk_score += 35
        predictions.append({
            "metric": "RAM",
            "current": f"{ram}%",
            "risk": "HIGH",
            "prediction": "Memory leak detected by AI. Application usage pattern is abnormal.",
            "confidence": 0.88
        })
    elif ram > 80:
        risk_score += 25
        predictions.append({
            "metric": "RAM",
            "current": f"{ram}%",
            "risk": "HIGH",
            "prediction": "Memory pressure may cause application crashes",
            "confidence": 0.75
        })
    elif ram > 70:
        risk_score += 10
        predictions.append({
            "metric": "RAM",
            "current": f"{ram}%",
            "risk": "MEDIUM",
            "prediction": "Monitor memory usage closely",
            "confidence": 0.55
        })
    
    # Disk prediction
    if disk > 95:
        risk_score += 30
        predictions.append({
            "metric": "Disk",
            "current": f"{disk}%",
            "risk": "CRITICAL",
            "prediction": "System may fail to write logs or save files",
            "confidence": 0.85
        })
    elif disk > 85:
        risk_score += 20
        predictions.append({
            "metric": "Disk",
            "current": f"{disk}%",
            "risk": "HIGH",
            "prediction": "Disk cleanup recommended soon",
            "confidence": 0.70
        })
    
    # Overall risk assessment
    if risk_score >= 70:
        overall_risk = "CRITICAL"
    elif risk_score >= 50:
        overall_risk = "HIGH"
    elif risk_score >= 30:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"
    
    return {
        "risk_score": min(risk_score, 100),
        "overall_risk": overall_risk,
        "predictions": predictions,
        "recommendations": _generate_recommendations(cpu, ram, disk)
    }

def _generate_recommendations(cpu, ram, disk):
    """Generate actionable recommendations"""
    recommendations = []
    
    if cpu > 75:
        recommendations.append({
            "action": "boost_ram",
            "priority": "HIGH",
            "description": "Free RAM to reduce CPU load from memory management"
        })
        recommendations.append({
            "action": "kill_high_cpu",
            "priority": "HIGH",
            "description": "Terminate high CPU processes"
        })
    
    if ram > 80:
        recommendations.append({
            "action": "boost_ram",
            "priority": "CRITICAL",
            "description": "Immediately free RAM to prevent system slowdown"
        })
    
    if disk > 85:
        recommendations.append({
            "action": "clean_junk",
            "priority": "HIGH",
            "description": "Clean temporary files to free disk space"
        })
    
    if not recommendations:
        recommendations.append({
            "action": "monitor",
            "priority": "LOW",
            "description": "System is healthy, continue monitoring"
        })
    
    return recommendations

def auto_apply_fixes(cpu, ram, disk):
    """Auto-apply optimizations based on current metrics"""
    applied_fixes = []
    results = []
    
    # Auto-apply RAM boost if RAM > 80%
    if ram > 80:
        try:
            freed_mb = _auto_boost_ram()
            applied_fixes.append("boost_ram")
            results.append({
                "fix": "RAM Boost",
                "status": "success",
                "details": f"Freed {freed_mb:.2f} MB"
            })
        except Exception as e:
            results.append({
                "fix": "RAM Boost",
                "status": "failed",
                "details": str(e)
            })
    
    # Auto-clean junk files if disk > 85%
    if disk > 85:
        try:
            freed_mb = _auto_clean_junk()
            applied_fixes.append("clean_junk")
            results.append({
                "fix": "Junk File Cleanup",
                "status": "success",
                "details": f"Freed {freed_mb:.2f} MB"
            })
        except Exception as e:
            results.append({
                "fix": "Junk File Cleanup",
                "status": "failed",
                "details": str(e)
            })
    
    # Auto-kill high CPU processes if CPU > 85%
    if cpu > 85:
        try:
            killed = _auto_kill_high_cpu()
            applied_fixes.append("kill_high_cpu")
            results.append({
                "fix": "High CPU Process Termination",
                "status": "success",
                "details": f"Terminated {killed} processes"
            })
        except Exception as e:
            results.append({
                "fix": "High CPU Process Termination",
                "status": "failed",
                "details": str(e)
            })
    
    return {
        "success": len(applied_fixes) > 0,
        "applied_fixes": applied_fixes,
        "results": results,
        "message": f"Auto-applied {len(applied_fixes)} optimization(s)"
    }

def _auto_boost_ram():
    """Internal function to boost RAM"""
    safe_to_kill = [
        "chrome.exe", "firefox.exe", "edge.exe", "opera.exe",
        "discord.exe", "spotify.exe", "steam.exe"
    ]
    
    freed_mb = 0
    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            proc_name = proc.info['name'].lower()
            if any(safe in proc_name for safe in safe_to_kill):
                mem_mb = proc.info['memory_info'].rss / (1024*1024)
                proc.terminate()
                freed_mb += mem_mb
        except:
            pass
    
    return freed_mb

def _auto_clean_junk():
    """Internal function to clean junk files"""
    freed_mb = 0
    temp_dirs = [
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
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
                        freed_mb += size / (1024*1024)
                    except:
                        pass
        except:
            pass
    
    return freed_mb

def _auto_kill_high_cpu():
    """Internal function to kill high CPU processes"""
    killed = 0
    safe_to_kill = [
        "chrome.exe", "firefox.exe", "edge.exe", "opera.exe",
        "discord.exe", "spotify.exe", "steam.exe"
    ]
    
    for proc in psutil.process_iter(['name', 'cpu_percent']):
        try:
            cpu = proc.cpu_percent(interval=None)
            proc_name = proc.info['name'].lower()
            if cpu > 50 and any(safe in proc_name for safe in safe_to_kill):
                proc.terminate()
                killed += 1
        except:
            pass
    
    return killed
