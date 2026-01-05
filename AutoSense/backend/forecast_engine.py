import random
from datetime import datetime, timedelta

def predict_health(cpu, ram, disk):
    # Simulate a sophisticated time-series forecast
    # In production, this would use the History DB
    
    predictions = []
    current_time = datetime.now()
    
    trend = "STABLE"
    if cpu > 80: trend = "DEGRADING"
    
    for i in range(1, 6): # Next 5 hours
        time_slot = (current_time + timedelta(hours=i)).strftime("%H:00")
        
        # Simulate prediction logic
        pred_cpu = cpu + random.randint(-5, 10)
        pred_risk = "LOW"
        if pred_cpu > 90: pred_risk = "CRITICAL"
        elif pred_cpu > 70: pred_risk = "MEDIUM"
        
        predictions.append({
            "time": time_slot,
            "predicted_cpu": max(0, min(100, pred_cpu)),
            "risk_level": pred_risk,
            "confidence": f"{random.randint(85, 99)}%"
        })
        
    return {
        "current_trend": trend,
        "forecast": predictions,
        "recommendation": "Enable Auto-Mode" if trend == "DEGRADING" else "System looking good"
    }
