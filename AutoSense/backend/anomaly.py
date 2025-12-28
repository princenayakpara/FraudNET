from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.history = []
        self.model = IsolationForest(contamination=0.1)

    def update(self, value):
        self.history.append(value)
        if len(self.history) > 30:
            self.history.pop(0)
        if len(self.history) >= 10:
            self.model.fit([[v] for v in self.history])

    def detect(self, value):
        if len(self.history) < 10:
            return False
        return self.model.predict([[value]])[0] == -1
