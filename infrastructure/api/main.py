import sys
import os

# 1. PATH FIX: Ensures the 'src' folder is discoverable
sys.path.append(os.getcwd())

# Change this if it has an 's' at the end in your code but not on disk
from src.application.interface import AbstractModel
from fastapi import FastAPI, HTTPException
from src.domain.entities import Transaction
from src.domain.data_structures import CircularBuffer, IPBlacklistTrie, HyperLogLog
from src.application.detector import AnomalyDetector
from src.infrastructure.ml_models.onnx_impl import ONNXModel

# 2. INITIALIZATION (The "Production" setup)
app = FastAPI(title="SentinelStream: Production Anomaly Engine")

# Load the ONNX model we trained earlier
# Path assumes you are running from the sentinel_stream/ directory
onnx_path = os.path.join("models", "fraud_model.onnx")
if not os.path.exists(onnx_path):
    raise RuntimeError(f"Model not found at {onnx_path}. Did you run train_model.py?")

# Initialize our specialized components
model = ONNXModel(onnx_path)
history = CircularBuffer(size=1000)      # Track last 1000 tx for velocity
blacklist = IPBlacklistTrie()            # Instant prefix-matching
unique_users = HyperLogLog(b=10)         # Memory-efficient cardinality

# The Detector coordinates between the state (history) and the model
detector = AnomalyDetector(model=model, history_buffer=history)

# Pre-populate a blacklist for demonstration
blacklist.insert("192.168.1.100")
blacklist.insert("10.0.0.5")

# 3. ENDPOINTS
@app.get("/")
def health_check():
    return {
        "status": "active",
        "engine": "ONNX Runtime",
        "optimizations": ["Trie", "HyperLogLog", "CircularBuffer"]
    }

@app.post("/detect")
async def detect_transaction(tx: Transaction):
    """
    Main pipeline: Blacklist -> Feature Engineering -> Inference
    """
    # Step A: Update global cardinality (How many unique users have we seen?)
    unique_users.add(tx.user_id)
    
    # Step B: Layer 1 Defense (Trie Blacklist) - O(L) Complexity
    if blacklist.is_blacklisted(tx.ip_address):
        return {
            "status": "REJECTED",
            "reason": "IP_IN_BLACKLIST",
            "score": 1.0,
            "user_stats": {"unique_users_seen": unique_users.count()}
        }

    # Step C: Layer 2 Defense (ML Inference) - ONNX Optimized
    try:
        # The detector handles the CircularBuffer update and the ONNX call
        result = detector.process(tx.amount, tx.ip_address)
        
        return {
            "status": "ACCEPTED" if not result["is_anomaly"] else "FLAGGED",
            "fraud_score": result["score"],
            "features": {
                "velocity_1m": result["velocity_1m"],
                "current_amount": tx.amount
            },
            "user_stats": {
                "unique_users_seen": unique_users.count()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)