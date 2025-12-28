def generate_report(metrics, score, anomaly, fixes):
    return {
        "metrics": metrics,
        "health_score": score,
        "anomaly": anomaly,
        "fixes": fixes
    }
