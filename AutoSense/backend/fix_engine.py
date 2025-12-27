import psutil
from control import get_blacklist
from notifier import send_alert
from alert_manager import should_alert

WHITELIST = ["system", "explorer.exe", "python.exe", "chrome.exe"]

def auto_fix(anomaly):
    if not anomaly:
        return []

    bl = [b.lower() for b in get_blacklist()["apps"]]
    killed = []

    # Warm-up CPU counters
    for p in psutil.process_iter():
        try:
            p.cpu_percent()
        except:
            pass

    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            name = proc.info['name']
            if not name:
                continue

            lname = name.lower()
            cpu = proc.cpu_percent(interval=0.1)
            mem = proc.info['memory_percent']

            if lname in bl and lname not in WHITELIST:
                if cpu > 25 or mem > 20:
                    psutil.Process(proc.info['pid']).terminate()
                    killed.append(name)

        except:
            pass

    # Alert only when state changes + cooldown
    if killed and should_alert(1):
        send_alert("AutoSense Alert", f"Terminated: {', '.join(killed)}")

    return killed
