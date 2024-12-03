from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class SensorData(BaseModel):
    temperature: Optional[float] = None
    noise: Optional[float]
    light: Optional[float] = None
    timestamp: datetime = datetime.now()