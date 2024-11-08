from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    temperature: float
    co2: int
    timestamp: datetime = datetime.utcnow()