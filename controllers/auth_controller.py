# controllers/auth_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from schemas.auth_schema import (
    UserRegisterSchema, 
    AdminRegisterSchema, 
    UserLoginSchema, 
    TokenSchema
)
from services.auth_service import AuthService
from dependencies.auth_dependencies import get_current_user
from models.user import User


class AuthController:
    """Controller for authentication operations"""
    
    def __init__(self):
        self.router = APIRouter(prefix="/auth", tags=["Authentication"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all authentication routes"""
        
        @self.router.post("/register", response_model=TokenSchema, status_code=201)
        def register_customer(
            user_data: UserRegisterSchema,
            db: Session = Depends(get_db)
        ):
            """Registro de nuevos clientes"""
            service = AuthService(db)
            return service.register_customer(user_data)
        
        @self.router.post("/register-admin", response_model=TokenSchema, status_code=201)
        def register_admin(
            admin_data: AdminRegisterSchema,
            db: Session = Depends(get_db)
        ):
            """Registro de administradores con código secreto"""
            service = AuthService(db)
            return service.register_admin(admin_data)
        
        @self.router.post("/login", response_model=TokenSchema)
        def login(
            credentials: UserLoginSchema,
            db: Session = Depends(get_db)
        ):
            """Login para clientes y administradores"""
            service = AuthService(db)
            return service.login(credentials)
        
        @self.router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            """Obtiene información del usuario actual"""
            user_data = current_user.to_dict()
            
            # Si es cliente, agregar datos del cliente
            if current_user.client:
                user_data["client"] = current_user.client.to_dict()
            
            return user_data