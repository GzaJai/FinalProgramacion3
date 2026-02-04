from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = "customer"  # Valor por defecto

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool = True
    
    class Config:
        from_attributes = True  # Para convertir desde SQLAlchemy models

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: int
    email: str
    role: str