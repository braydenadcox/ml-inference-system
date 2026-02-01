import numpy as np

class DummyModel:
    def predict(self, input_data):
        return [0.5] * len(input_data)  # Dummy prediction
    
    def predict_proba(self, input_data):
        num_samples = len(input_data)
        return np.array([[0.5, 0.5]] * len(input_data))  # Dummy probabilities===