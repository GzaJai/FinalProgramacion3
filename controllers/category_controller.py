from fastapi import Depends
from sqlalchemy.orm import Session

from controllers.base_controller_impl import BaseControllerImpl
from schemas.category_schema import CategorySchema
from services.category_service import CategoryService
from config.database import get_db
from dependencies.auth_dependencies import require_admin
from models.user import User


class CategoryController(BaseControllerImpl):
    """Controller for Category entity with CRUD operations."""

    def __init__(self):
        super().__init__(
            schema=CategorySchema,
            service_factory=lambda db: CategoryService(db),
            tags=["Categories"]
        )
        
        # Sobrescribir rutas POST, PUT, DELETE para agregar protección de admin
        
        @self.router.post("/", response_model=CategorySchema)
        def create_category_protected(
            category_data: CategorySchema,
            db: Session = Depends(get_db),
            current_user: User = Depends(require_admin)  # 👈 SOLO ADMINS
        ):
            """Crear categoría - SOLO ADMINS"""
            service = CategoryService(db)
            return service.save(category_data)
        
        @self.router.put("/{id}", response_model=CategorySchema)
        def update_category_protected(
            id: int,  # 👈 Usar 'id' no 'id_key'
            category_data: CategorySchema,
            db: Session = Depends(get_db),
            current_user: User = Depends(require_admin)  # 👈 SOLO ADMINS
        ):
            """Actualizar categoría - SOLO ADMINS"""
            service = CategoryService(db)
            return service.update(id, category_data)
        
        @self.router.delete("/{id}", status_code=204)
        def delete_category_protected(
            id: int,  # 👈 Usar 'id' no 'id_key'
            db: Session = Depends(get_db),
            current_user: User = Depends(require_admin)  # 👈 SOLO ADMINS
        ):
            """Eliminar categoría - SOLO ADMINS"""
            service = CategoryService(db)
            service.delete(id)
            return None