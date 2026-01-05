def calculate_health(cpu, ram, disk, anomaly=False):
    score = 100
    score -= cpu * 0.3
    score -= ram * 0.3
    score -= disk * 0.2

    if anomaly:
        score -= 15

    return max(int(score), 0)
