from src.application.interfaces import AbstractModel
from src.domain.data_structures import CircularBuffer

class AnomalyDetector:
    def __init__(self, model: AbstractModel, history_buffer: CircularBuffer):
        self.model = model
        self.history = history_buffer

    def process(self, amount: float, ip_address: str) -> dict:
        # 1. Feature Engineering: Get velocity from Circular Buffer
        velocity_1m = self.history.get_velocity(window_seconds=60)
        
        # 2. Update the buffer with current transaction
        self.history.add(amount)
        
        # 3. ML Inference
        score = self.model.predict([amount, velocity_1m])
        
        return {
            "is_anomaly": score > 0.5,
            "score": score,
            "velocity_1m": velocity_1m
        }