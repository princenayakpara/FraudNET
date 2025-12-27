def calculate_health(cpu, ram, disk, anomaly):
    score = 100
    score -= cpu * 0.4
    score -= ram * 0.3
    score -= disk * 0.2
    if anomaly:
        score -= 15

    return max(int(score), 5)
