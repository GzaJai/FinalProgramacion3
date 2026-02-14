from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.address_schema import AddressSchema
    from schemas.order_schema import OrderSchema


class ClientSchema(BaseSchema):
    """Schema for Client entity with validations."""
    
    name: str = Field(..., min_length=1, max_length=200)
    lastname: str = Field(..., min_length=1, max_length=200)  # ← NUEVO CAMPO
    email: Optional[str] = Field(None, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    telephone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-()]+$')
    
    # Relaciones opcionales
    addresses: Optional[List['AddressSchema']] = []
    orders: Optional[List['OrderSchema']] = []