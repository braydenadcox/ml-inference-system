class DummyModel:
    def predict(self, input_data):
        return [0.5] * len(input_data)  # Dummy prediction