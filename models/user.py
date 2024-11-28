from pydantic import BaseModel, EmailStr

# Modelo para los datos de entrada (registro)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Modelo para la respuesta (sin incluir la contraseña)
class UserResponse(BaseModel):
    id: str
    email: EmailStr
