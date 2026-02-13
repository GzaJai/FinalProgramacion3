# schemas/category_schema.py
from pydantic import BaseModel, Field, computed_field
from typing import Optional


class CategorySchema(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1)
    
    # 👇 Campo calculado que devuelve el mismo valor que id
    @computed_field
    @property
    def id_key(self) -> Optional[int]:
        return self.id
    
    class Config:
        from_attributes = True