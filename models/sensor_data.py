from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    temperature: float
    noise: float
    light: float
    timestamp: datetime = datetime.now()