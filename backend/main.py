from database.mongo import get_db
db = get_db()


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

    record = {
        "amount": tx.amount,
        "device_trust": tx.device_trust,
        "country": tx.country,
        "home_country": tx.home_country,
        "hour": tx.hour,
        "rule_score": rule_score,
        "ml_score": ml_score,
        "final_score": final_score
    }

    db.transactions.insert_one(record)

    return {
        "status": "fraud" if final_score > 60 else "safe",
        "final_score": final_score,
        "rule_score": rule_score,
        "ml_score": ml_score
    }

@app.get("/transactions")
def get_transactions():
    txs = list(db.transactions.find({}, {"_id": 0}))
    return txs
