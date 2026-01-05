from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.history = []
        self.model = IsolationForest(contamination=0.05)
        self.trained = False

    def update_history(self, value):
        self.history.append([float(value)])

        if len(self.history) > 100:
            self.history.pop(0)

        if len(self.history) >= 20:
            self.model.fit(self.history)
            self.trained = True

    def z_score_anomaly(self, value):
        if len(self.history) < 10:
            return False

        values = [x[0] for x in self.history]
        mean = sum(values) / len(values)
        std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5

        if std == 0:
            return False

        z = abs((value - mean) / std)
        return z > 3

    def isolation_forest_anomaly(self, value):
        if not self.trained:
            return False

        return bool(self.model.predict([[float(value)]])[0] == -1)
