#!/bin/bash

echo "🚀 Starting FraudNET backend setup..."

# go to backend folder
cd backend

echo "📌 Creating virtual environment..."
python -m venv venv

echo "📌 Activating virtual environment..."
# Windows
if [[ "$OS" == "Windows_NT" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "📦 Installing dependencies..."
pip install fastapi uvicorn pandas scikit-learn joblib pydantic

echo "✔ Saving requirements..."
pip freeze > requirements.txt

echo "📁 Creating folder structure (if missing)..."
mkdir -p rules models api

echo "📄 Creating default backend files..."

# main API file
cat << 'EOF' > main.py
from fastapi import FastAPI
from api.transactions import Transaction
from rules.rule_engine import rule_engine
from models.model_loader import model

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FraudNET Backend Running"}

@app.post("/score")
def score_transaction(tx: Transaction):
    rule_score = rule_engine(tx)
    ml_score = model.predict_proba([[tx.amount, tx.hour]])[0][1] * 100
    final_score = (rule_score + ml_score) / 2

    return {
        "rule_score": rule_score,
        "ml_score": ml_score,
        "final_score": final_score,
        "status": "fraud" if final_score > 60 else "safe"
    }
EOF

# rule engine
cat << 'EOF' > rules/rule_engine.py
def rule_engine(tx):
    score = 0
    if tx.amount > 50000:
        score += 40
    if tx.device_trust == "low":
        score += 30
    if tx.country != tx.home_country:
        score += 20
    if 0 <= tx.hour <= 5:
        score += 10
    return score
EOF

# pydantic schema
cat << 'EOF' > api/transactions.py
from pydantic import BaseModel

class Transaction(BaseModel):
    amount: float
    device_trust: str
    country: str
    home_country: str
    hour: int
EOF

# dummy ML model
cat << 'EOF' > models/model_loader.py
class DummyModel:
    def predict_proba(self, X):
        return [[0.3, 0.7]]  # example probability (70% risk)

model = DummyModel()
EOF

echo "🚀 Starting server..."
uvicorn main:app --reload
