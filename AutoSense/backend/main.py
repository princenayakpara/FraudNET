from monitor import collect_metrics
from anomaly import AnomalyDetector
from health_score import calculate_health
from fix_engine import suggest_fixes
from report import generate_report
import time

detector = AnomalyDetector()

while True:
    metrics = collect_metrics()

    cpu = metrics["cpu"]
    ram = metrics["ram"]
    disk = metrics["disk"]

    detector.update_history(cpu)

    z_anomaly = detector.z_score_anomaly(cpu)
    ml_anomaly = detector.isolation_forest_anomaly(cpu)

    anomaly_detected = z_anomaly or ml_anomaly

    health = calculate_health(cpu, ram, disk, anomaly_detected)
    fixes = suggest_fixes(cpu, ram, disk)

    report = generate_report(metrics, health, anomaly_detected, fixes)

    print(report)

    time.sleep(5)
