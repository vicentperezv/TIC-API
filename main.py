from fastapi import FastAPI, HTTPException, Depends, Header, Query
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os
import pandas as pd
import numpy as np
from models.sensor_data import SensorData

from database import sensor_collection  # Importa la colección "sensor" configurada

app = FastAPI()


# Cargar la API Key desde las variables de entorno
API_KEY = os.getenv("API_KEY")

# Dependencia para verificar la API Key
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")



# Endpoint para agregar datos del sensor a la colección "sensor"
@app.post("/sensor-data", dependencies=[Depends(verify_api_key)])
async def add_sensor_data(data: SensorData):
    try:
        # Inserta los datos en la colección "sensor"
        result = await sensor_collection.insert_one(data.dict())
        return {"status": "Data inserted", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inserting data")



# Endpoint para obtener las últimas 10 inserciones
@app.get("/sensor-data/recent", response_model=List[SensorData],dependencies=[Depends(verify_api_key)] )
async def get_recent_sensor_data():
    try:
        # Obtiene los últimos 10 documentos, ordenados por timestamp en orden descendente
        recent_data = await sensor_collection.find().sort("timestamp", -1).limit(10).to_list(length=10)
        return recent_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
        

# Endpoint para obtener el promedio de temperatura y CO2 en un rango de fechas
@app.get("/sensor-data/average", dependencies=[Depends(verify_api_key)])
async def get_average_sensor_data(
    start_date: datetime = Query(..., description="Fecha de inicio"),
    end_date: datetime = Query(..., description="Fecha de fin")
):
    try:
        # Filtra los datos en el rango de fechas especificado
        data = await sensor_collection.find({
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found in the given date range")
        
        # Convierte los datos en un DataFrame de Pandas
        df = pd.DataFrame(data)
        
        # Calcula los promedios usando pandas
        avg_temperature = df["temperature"].mean()
        avg_co2 = df["co2"].mean()

        return {
            "average_temperature": avg_temperature,
            "average_co2": avg_co2,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error calculating average data")

# Endpoint para obtener todos los datos en un rango de fechas
@app.get("/sensor-data/range", response_model=List[SensorData], dependencies=[Depends(verify_api_key)])
async def get_sensor_data_in_range(
    start_date: datetime = Query(..., description="Fecha de inicio"),
    end_date: datetime = Query(..., description="Fecha de fin")
):
    try:
        # Filtra los datos en el rango de fechas especificado
        data = await sensor_collection.find({
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found in the given date range")
        
        # Devuelve todos los datos encontrados en el rango de fechas
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving data")



# Endpoint para obtener el valor máximo de temperatura y CO2 en un rango de fechas
@app.get("/sensor-data/max", dependencies=[Depends(verify_api_key)])
async def get_max_sensor_data(
    start_date: datetime = Query(..., description="Fecha de inicio"),
    end_date: datetime = Query(..., description="Fecha de fin")
):
    try:
        # Filtra los datos en el rango de fechas especificado
        data = await sensor_collection.find({
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found in the given date range")
        
        # Convierte los datos en un DataFrame de Pandas
        df = pd.DataFrame(data)
        
        # Encuentra los valores máximos usando pandas
        max_temperature = df["temperature"].max()
        max_co2 = df["co2"].max()

        return {
            "max_temperature": max_temperature,
            "max_co2": max_co2,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving max data")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


