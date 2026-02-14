# services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User, UserRole
from models.client import ClientModel
from schemas.auth_schema import UserRegisterSchema, AdminRegisterSchema, UserLoginSchema
from auth.jwt_handler import create_access_token


class AuthService:
    """Service for authentication operations"""
    
    ADMIN_SECRET_CODE = "ADMIN2024SECRET"
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_customer(self, user_data: UserRegisterSchema) -> dict:
        """Registra un nuevo cliente"""
        # Verificar si el email ya existe
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        
        try:
            # Crear usuario
            new_user = User(
                email=user_data.email,
                name=user_data.name,  # ← AGREGADO
                lastname=user_data.lastname,  # ← AGREGADO
                role=UserRole.CUSTOMER
            )
            new_user.set_password(user_data.password)
            self.db.add(new_user)
            self.db.flush()
            
            # Crear cliente asociado (si todavía lo necesitas)
            new_client = ClientModel(
                user_id=new_user.id,
                name=user_data.name,
                lastname=user_data.lastname,  # ← AGREGADO si Client también tiene lastname
                phone=user_data.phone
            )
            self.db.add(new_client)
            self.db.commit()
            self.db.refresh(new_user)
            
            # Crear token
            access_token = create_access_token(
                data={"user_id": new_user.id, "role": new_user.role.value}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": new_user.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar usuario: {str(e)}"
            )
    
    def register_admin(self, admin_data: AdminRegisterSchema) -> dict:
        """Registra un nuevo administrador"""
        # Verificar código secreto
        if admin_data.codigo_admin != self.ADMIN_SECRET_CODE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Código de administrador incorrecto"
            )
        
        # Verificar si el email ya existe
        existing_user = self.db.query(User).filter(User.email == admin_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está registrado"
            )
        
        try:
            # Crear administrador
            new_admin = User(
                email=admin_data.email,
                name=admin_data.name,  # ← AGREGADO
                lastname=admin_data.lastname,  # ← AGREGADO
                role=UserRole.ADMIN
            )
            new_admin.set_password(admin_data.password)
            self.db.add(new_admin)
            self.db.commit()
            self.db.refresh(new_admin)
            
            # Crear token
            access_token = create_access_token(
                data={"user_id": new_admin.id, "role": new_admin.role.value}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": new_admin.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar administrador: {str(e)}"
            )
    
    def login(self, credentials: UserLoginSchema) -> dict:
        """Login para clientes y administradores"""
        # Buscar usuario por email
        user = self.db.query(User).filter(User.email == credentials.email).first()
        
        if not user or not user.check_password(credentials.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está desactivada"
            )
        
        # Crear token
        access_token = create_access_token(
            data={"user_id": user.id, "role": user.role.value}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }