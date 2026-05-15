import sys
import os

# 1. Setup Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from fastapi import FastAPI, HTTPException

# 2. Synchronized Imports
try:
    # Ensure this matches your filename: interfaces.py
    from src.application.interfaces import AbstractModel 
    from src.domain.entities import Transaction
    from src.domain.data_structures import CircularBuffer, IPBlacklistTrie, HyperLogLog
    from src.application.detector import AnomalyDetector
    from src.infrastructure.ml_models.onnx_impl import ONNXModel
    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import failed. Error: {e}")
    sys.exit(1)

# 3. Initialization
app = FastAPI(title="SentinelStream Engine")
onnx_path = os.path.join(BASE_DIR, "models", "fraud_model.onnx")

model = ONNXModel(onnx_path)
history = CircularBuffer(size=1000)
blacklist = IPBlacklistTrie()
unique_users = HyperLogLog(b=10)
detector = AnomalyDetector(model=model, history_buffer=history)

@app.post("/detect")
async def detect(tx: Transaction):
    unique_users.add(tx.user_id)
    if blacklist.is_blacklisted(tx.ip_address):
        return {"status": "REJECTED", "reason": "BLACKLIST"}
    
    result = detector.process(tx.amount, tx.ip_address)
    return {
        "status": "ACCEPTED" if not result["is_anomaly"] else "FLAGGED",
        "fraud_score": result["score"],
        "user_stats": {"unique_users_seen": unique_users.count()}
    }

if __name__ == "__main__":
    print("🚀 SentinelStream API is starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)