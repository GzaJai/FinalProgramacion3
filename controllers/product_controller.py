# controllers/product_controller.py
"""Product controller with admin protection for write operations."""
from fastapi import Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from controllers.base_controller_impl import BaseControllerImpl
from schemas.product_schema import ProductSchema
from services.product_service import ProductService
from config.database import get_db
from dependencies.auth_dependencies import require_admin
from models.user import User


class ProductController(BaseControllerImpl):
    """Controller for Product entity with CRUD operations."""

    def __init__(self):
        super().__init__(
            schema=ProductSchema,
            service_factory=lambda db: ProductService(db),
            tags=["Products"]
        )
        
        # 👇 SOBRESCRIBIR GET BY ID (si necesitas personalizarlo)
        @self.router.get("/{id}", response_model=ProductSchema)
        def get_product_by_id(
            id: int,
            db: Session = Depends(get_db)
        ):
            """Obtener producto por ID - PÚBLICO"""
            service = ProductService(db)
            return service.get_one(id)
        
        # Sobrescribir ruta POST para agregar protección de admin
        @self.router.post("/", response_model=ProductSchema)
        def create_product_protected(
            name: str = Form(...),
            description: str = Form(...),
            price: float = Form(...),
            stock: int = Form(...),
            category_id: int = Form(...),
            image_url: Optional[str] = Form(None),
            image_public_id: Optional[str] = Form(None),
            db: Session = Depends(get_db),
            current_user: User = Depends(require_admin)
        ):
            """Crear producto - SOLO ADMINS"""
            product_data = ProductSchema(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id,
                image_url=image_url,
                image_public_id=image_public_id
            )
            
            service = ProductService(db)
            return service.save(product_data)
        
        # Sobrescribir ruta PUT para agregar protección de admin
        @self.router.put("/{id}", response_model=ProductSchema)
        def update_product_protected(
            id: int,
            product_data: ProductSchema,
            db: Session = Depends(get_db),
            current_user: User = Depends(require_admin)
        ):
            """Actualizar producto - SOLO ADMINS"""
            service = ProductService(db)
            return service.update(id, product_data)
        
        # Sobrescribir ruta DELETE para agregar protección de admin
        @self.router.delete("/{id}", status_code=204)
        def delete_product_protected(
            id: int,
            db: Session = Depends(get_db),
            current_user: User = Depends(require_admin)
        ):
            """Eliminar producto - SOLO ADMINS"""
            service = ProductService(db)
            service.delete(id)
            return None