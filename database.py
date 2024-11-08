from motor.motor_asyncio import AsyncIOMotorClient
import os

# Lee la URL de conexión desde una variable de entorno
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Crear cliente y base de datos
client = AsyncIOMotorClient(MONGO_DB_URL)
client = AsyncIOMotorClient(MONGO_DB_URL)
db = client["TIC"]  # Selecciona la base de datos "TIC"
sensor_collection = db["sensor"]  # Selecciona la colección "sensor"