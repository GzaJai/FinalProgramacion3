# schemas/auth_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from models.user import UserRole


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)
    phone: Optional[str] = None


class AdminRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    codigo_admin: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponseSchema(BaseModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True