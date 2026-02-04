# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import bcrypt
import hashlib
import enum

from models.base_model import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    client = relationship(
        "ClientModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    @staticmethod
    def _normalize_password(password: str) -> bytes:
        """
        Normaliza la contraseña usando SHA256 antes de bcrypt.
        Esto permite contraseñas de cualquier longitud.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

    def set_password(self, password: str):
        """Hashea y guarda la contraseña"""
        normalized_password = self._normalize_password(password)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(normalized_password, salt)
        self.password_hash = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        normalized_password = self._normalize_password(password)
        return bcrypt.checkpw(normalized_password, self.password_hash.encode('utf-8'))

    def to_dict(self):
        """Serializa el usuario (sin exponer el hash de contraseña)"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') else None
        }