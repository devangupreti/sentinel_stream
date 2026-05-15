import onnxruntime as rt
import numpy as np
from src.application.interfaces import AbstractModel

class ONNXModel(AbstractModel):
    def __init__(self, model_path: str):
        # Explicitly using CPU provider for local execution
        self.sess = rt.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.sess.get_inputs()[0].name

    def predict(self, features: list) -> float:
        # features: [amount, velocity]
        input_data = np.array([features], dtype=np.float32)
        
        # Run inference
        outputs = self.sess.run(None, {self.input_name: input_data})
        
        # IsolationForest returns -1 for anomaly, 1 for normal
        label = outputs[0][0]
        
        return 0.95 if label == -1 else 0.10
