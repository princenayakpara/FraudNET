def generate_report(metrics, health, anomaly_detected, fixes):

    if health >= 80:
        status = "Healthy"
    elif health >= 50:
        status = "Warning"
    else:
        status = "Critical"

    return {
        "cpu": float(metrics["cpu"]),
        "ram": float(metrics["ram"]),
        "disk": float(metrics["disk"]),
        "health_score": float(health),
        "health_status": status,
        "anomaly": bool(anomaly_detected),
        "fixes": list(map(str, fixes))
    }
