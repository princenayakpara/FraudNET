class DummyModel:
    def predict_proba(self, X):
        return [[0.3, 0.7]]  # example probability (70% risk)

model = DummyModel()
