from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import threading

from monitor import log_stats, get_stats
from health_score import calculate_health
from anomaly import detect_anomaly
from control import add_blacklist, get_blacklist
from fix_engine import auto_fix
from notifier import send_alert
from alert_manager import should_alert
from report import generate_report

app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Background system logger
threading.Thread(target=log_stats, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/stats")
def stats():
    return get_stats()


@app.get("/health")
def health():
    stats = get_stats()

    cpu = stats["cpu"]
    ram = stats["ram"]
    disk = stats["disk"]

    anomaly = detect_anomaly(cpu, ram, disk)

    if should_alert(anomaly) and anomaly:
        send_alert("AutoSense Warning", "Unusual system behavior detected!")

    killed = auto_fix(anomaly)

    score = calculate_health(cpu, ram, disk, anomaly)
    status = "System Normal" if score > 70 else "System At Risk"

    return {
        "score": score,
        "status": status,
        "anomaly": anomaly,
        "killed": killed
    }


@app.get("/blacklist/{app_name}")
def blacklist(app_name: str):
    add_blacklist(app_name)
    return {"message": f"{app_name} added to blacklist"}


@app.get("/blacklist")
def fetch_blacklist():
    return JSONResponse(get_blacklist())


@app.get("/report")
def report():
    file = generate_report()
    return FileResponse(file, filename="AutoSense_Report.pdf")
