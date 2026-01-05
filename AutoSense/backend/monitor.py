import psutil

def collect_metrics():
    # Set interval to None to avoid blocking for 1 second.
    # We rely on previous calls to determine the percentage.
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    return {
        "cpu": round(cpu, 2),
        "ram": round(ram, 2),
        "disk": round(disk, 2)
    }
