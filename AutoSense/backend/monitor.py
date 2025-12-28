import psutil

def collect_metrics():
    net = psutil.net_io_counters()
    return {
        "cpu": round(psutil.cpu_percent(interval=1), 1),
        "ram": round(psutil.virtual_memory().percent, 1),
        "disk": round(psutil.disk_usage('/').percent, 1),
        "network": net.bytes_sent + net.bytes_recv
    }
