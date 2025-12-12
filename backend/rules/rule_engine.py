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
