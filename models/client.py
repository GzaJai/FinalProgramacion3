from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class ClientModel(BaseModel):
    __tablename__ = "clients"

    # NO pongas 'id' aquí, ya viene de BaseModel
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    address = Column(String(500))
    
    # FK a users - nullable=True permite clientes sin usuario
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),  # Si borras user, user_id = NULL
        nullable=True, 
        unique=True  # Un usuario solo puede tener un cliente
    )

    # Relación
    user = relationship("User", back_populates="client")
    
    # Otras relaciones existentes
    orders = relationship("OrderModel", back_populates="client")
    addresses = relationship("AddressModel", back_populates="client")
    bills = relationship("BillModel", back_populates="client")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.user.email if self.user else None,
        }