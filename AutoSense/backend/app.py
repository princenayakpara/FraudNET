from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os, time, csv

from monitor import collect_metrics
from anomaly import AnomalyDetector
from health_score import calculate_health
from fix_engine import suggest_fixes
from csv_logger import log_to_csv
from email_alert import send_alert

app = Flask(__name__)
CORS(app)

detector = AnomalyDetector()
START_TIME = time.time()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CSV_FILE = os.path.join(PROJECT_ROOT, "data", "system_metrics.csv")

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:file>")
def static_files(file):
    return send_from_directory(FRONTEND_DIR, file)

@app.route("/api/health")
def health():
    metrics = collect_metrics()
    detector.update(metrics["cpu"])
    anomaly = detector.detect(metrics["cpu"])

    score = calculate_health(
        metrics["cpu"], metrics["ram"], metrics["disk"], anomaly
    )

    fixes = suggest_fixes(
        metrics["cpu"], metrics["ram"], metrics["disk"]
    )

    alert = None
    if score < 90:
        alert = "🚨 CRITICAL: System health is very low!"
        try:
            send_alert(alert)
        except Exception as e:
            print("Email failed:", e)
    elif score < 60:
        alert = "⚠️ WARNING: System health is degrading"

    log_to_csv(metrics, score)

    uptime = int(time.time() - START_TIME)

    return jsonify({
        "metrics": metrics,
        "health_score": score,
        "anomaly": anomaly,
        "fixes": fixes,
        "alert": alert,
        "uptime": uptime
    })

@app.route("/api/last-records")
def last_records():
    records = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)[-10:]

            for row in rows:
                records.append({
                    "timestamp": row.get("timestamp"),
                    "cpu": row.get("cpu"),
                    "ram": row.get("ram"),
                    "disk": row.get("disk"),
                    "health_score": row.get("health_score"),
                })

    return jsonify(records)


@app.route("/api/download-csv")
def download_csv():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
