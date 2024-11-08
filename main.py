from fastapi import FastAPI, HTTPException
from typing import Union
from database import sensor_collection
from models.sensor_data import SensorData
from typing import List

app = FastAPI()

@app.post("/sensor-data")
async def add_sensor_data(data: SensorData):
    try:
        # Guarda los datos en la colección "sensor_data"
        result = await sensor_collection.insert_one(data.dict())
        return {"status": "Data inserted", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")

# Endpoint para obtener las últimas 10 inserciones
@app.get("/sensor-data/recent", response_model=List[SensorData])
async def get_recent_sensor_data():
    try:
        # Obtiene los últimos 10 documentos, ordenados por timestamp en orden descendente
        recent_data = await sensor_collection.find().sort("timestamp", -1).limit(10).to_list(length=10)
        return recent_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
        


@app.get("/")
async def read_root():
    return {"Hello": "World"}


