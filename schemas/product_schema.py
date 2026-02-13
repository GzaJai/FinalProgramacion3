"""Product schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field, ConfigDict

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema
    from schemas.review_schema import ReviewSchema


class ProductSchema(BaseSchema):
    """Schema for Product entity with validations."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)

    image_url: Optional[str] = Field(
        default=None,
        description="Public URL of the product image"
    )

    image_public_id: Optional[str] = Field(
        default=None,
        description="Cloud provider image identifier"
    )

    category_id: int = Field(...)

    category: Optional['CategorySchema'] = None
    reviews: Optional[List['ReviewSchema']] = []