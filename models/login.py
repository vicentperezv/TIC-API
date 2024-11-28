from pydantic import BaseModel, EmailStr
# Modelo para los datos de entrada del login
class LoginData(BaseModel):
    email: EmailStr
    password: str

# Modelo para la respuesta del login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
