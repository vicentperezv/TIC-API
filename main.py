from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Optional
import os
import pandas as pd
import numpy as np
import bcrypt
from models.sensor_data import SensorData
from models.user import UserCreate, UserResponse
from models.login import LoginData, LoginResponse
from database import sensor_collection, users_collection 
import jwt

app = FastAPI()

origins = [
    "http://localhost:5173",  # Origen de tu app React
    "http://127.0.0.1:5173",
    "https://tic-front-production.up.railway.app" # Alias local
    # Agrega otros orígenes si necesitas
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


# Cargar la API Key desde las variables de entorno
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey") 

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
@app.get("/sensor-data/recent", response_model=List[SensorData] )
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
        avg_noise = df["noise"].mean()
        avg_light = df["light"].mean()

        return {
            "average_temperature": avg_temperature,
            "average_noise": avg_noise,
            "average_light": avg_light,
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
        max_noise = df["noise"].max()
        max_light = df["light"].max()


        return {
            "max_temperature": max_temperature,
            "max_noise": max_noise,
            "max_light": max_light,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving max data")


# Endpoint para crear una cuenta
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        # Verifica si el correo ya está registrado
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Encripta la contraseña
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        # Crea el usuario en la base de datos
        user_data = {"email": user.email, "password": hashed_password.decode("utf-8")}
        result = await users_collection.insert_one(user_data)

        # Devuelve el usuario creado (sin contraseña)
        return {"id": str(result.inserted_id), "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating user")

# Endpoint para el login
@app.post("/login", response_model=LoginResponse)
async def login(data: LoginData):
    try:
        # Busca al usuario por correo electrónico
        user = await users_collection.find_one({"email": data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verifica la contraseña
        is_valid_password = bcrypt.checkpw(data.password.encode("utf-8"), user["password"].encode("utf-8"))
        if not is_valid_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Genera un token JWT
        payload = {
            "sub": str(user["_id"]),
            "email": user["email"],
            "exp": datetime.utcnow() + timedelta(days=30)  # El token expira en 1 hora
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during login")

@app.get("/")
async def read_root():
    return { "api": "TIC API", "version": "0.5" }


