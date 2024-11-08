from motor.motor_asyncio import AsyncIOMotorClient
import os

# Lee la URL de conexión desde una variable de entorno
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Crear cliente y base de datos
client = AsyncIOMotorClient(MONGO_DB_URL)
db = client.get_database()  # Obtiene la base de datos por defecto
