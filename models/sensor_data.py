from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class SensorData(BaseModel):
    temperature: float
    noise: float
    light: Optional[float] = None
    timestamp: datetime = datetime.now()