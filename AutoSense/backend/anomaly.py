import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest

model = None

def train_model():
    global model
    conn = sqlite3.connect("autosense.db")
    df = pd.read_sql("SELECT cpu, ram, disk FROM system_stats ORDER BY id DESC LIMIT 1000", conn)

    if len(df) < 30:
        return None

    model = IsolationForest(contamination=0.1)
    model.fit(df)
    return model

def detect_anomaly(cpu, ram, disk):
    global model
    if model is None:
        train_model()
        return 0

    prediction = model.predict([[cpu, ram, disk]])[0]
    return 1 if prediction == -1 else 0
