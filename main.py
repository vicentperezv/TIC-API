from fastapi import FastAPI, HTTPException
from typing import Union
from database import db
from models.sensor_data import SensorData
app = FastAPI()

@app.post("/sensor-data")
async def add_sensor_data(data: SensorData):
    try:
        # Guarda los datos en la colección "sensor_data"
        result = await db["sensor_data"].insert_one(data.dict())
        return {"status": "Data inserted", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inserting data")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


