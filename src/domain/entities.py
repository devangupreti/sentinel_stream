from pydantic import BaseModel, Field
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float = Field(gt=0)
    ip_address: str
    timestamp: datetime = Field(default_factory=datetime.now)

class DetectionResult(BaseModel):
    is_anomaly: bool
    score: float
    reason: str | None = None