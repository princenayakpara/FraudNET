import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, "..")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CSV_FILE = os.path.join(DATA_DIR, "system_metrics.csv")

def log_to_csv(metrics, score):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "cpu", "ram", "disk", "network", "health_score"
            ])
        writer.writerow([
            datetime.now(),
            metrics["cpu"],
            metrics["ram"],
            metrics["disk"],
            metrics["network"],
            score
        ])
