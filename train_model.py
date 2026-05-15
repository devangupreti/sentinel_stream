import numpy as np
from sklearn.ensemble import IsolationForest
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import os

# 1. Generate Synthetic Data
X_train = np.random.rand(100, 2) * 100 
outliers = np.array([[5000, 10000], [4000, 8000], [9000, 20000]])
X_train = np.vstack([X_train, outliers])

# 2. Train the Model
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)

# 3. Define the Input Schema
# Features: [amount, velocity]
initial_type = [('float_input', FloatTensorType([None, 2]))]

# 4. Convert with Target Opset Fix (No zipmap needed for IsolationForest)
onx = convert_sklearn(
    model, 
    initial_types=initial_type,
    target_opset={'': 15, 'ai.onnx.ml': 3}
)

# 5. Save
os.makedirs("models", exist_ok=True)
with open("models/fraud_model.onnx", "wb") as f:
    f.write(onx.SerializeToString())

print("✅ Success! Model saved to models/fraud_model.onnx")