from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from schemas.user_schema import UserCreate, UserRead
from repositories.user_repository import UserRepository
from services.base_service_impl import BaseServiceImpl
from utils.auth_utils import get_password_hash, verify_password
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)


class UserService(BaseServiceImpl):
    """Service for User entity with authentication"""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=UserRepository,
            model=User,
            schema=UserRead,  # 👈 Cambio aquí
            db=db
        )

    def create_user(self, user_data: UserCreate) -> UserRead:
        """
        Crear usuario con password hasheado
        
        Raises:
            HTTPException 400: Si el email ya existe
        """
        # Verificar que email no exista
        if self._repository.email_exists(user_data.email):
            logger.warning(f"Intento de registro con email existente: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Hash de la contraseña
        password_hash = get_password_hash(user_data.password)
        
        # Crear modelo
        from models.user import UserRole
        user_model = User(
            email=user_data.email,
            password_hash=password_hash,
            role=UserRole.ADMIN if user_data.role == "admin" else UserRole.CUSTOMER,
            is_active=True
        )
        
        # Guardar
        db_user = self._repository.save(user_model)
        logger.info(f"Usuario creado: {db_user.email} (role: {db_user.role})")
        
        return UserRead(
            id=db_user.id,
            email=db_user.email,
            role=db_user.role.value,
            is_active=db_user.is_active
        )

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Autenticar usuario
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            User si credenciales válidas, None si no
        """
        user = self._repository.get_by_email(email)
        
        if not user:
            logger.warning(f"Intento de login con email no existente: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Intento de login con usuario inactivo: {email}")
            return None
        
        if not verify_password(password, user.password_hash):
            logger.warning(f"Contraseña incorrecta para: {email}")
            return None
        
        logger.info(f"Login exitoso: {email}")
        return user

    def get_by_email(self, email: str) -> Optional[UserRead]:
        """Obtener usuario por email"""
        user = self._repository.get_by_email(email)
        if user:
            return UserRead(
                id=user.id,
                email=user.email,
                role=user.role.value,
                is_active=user.is_active
            )
        return None

    def deactivate_user(self, user_id: int) -> UserRead:
        """Desactivar usuario (soft delete)"""
        user = self._repository.get_one(user_id)
        user.is_active = False
        updated_user = self._repository.update(user)
        logger.info(f"Usuario desactivado: {user.email}")
        
        return UserRead(
            id=updated_user.id,
            email=updated_user.email,
            role=updated_user.role.value,
            is_active=updated_user.is_active
        )