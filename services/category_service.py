import logging
from typing import List
from sqlalchemy.orm import Session

from models.category import CategoryModel
from repositories.category_repository import CategoryRepository
from schemas.category_schema import CategorySchema
from services.base_service_impl import BaseServiceImpl
from services.cache_service import cache_service
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)


class CategoryService(BaseServiceImpl):
    """Service for Category entity with aggressive caching (rarely changes)."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=CategoryRepository,
            model=CategoryModel,
            schema=CategorySchema,
            db=db
        )
        self.cache = cache_service
        self.cache_prefix = "categories"
        self.cache_ttl = 3600

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CategorySchema]:
        """Get all categories with long-lived cache (SAFE VERSION)"""

        cache_key = self.cache.build_key(
            self.cache_prefix,
            "list",
            skip=skip,
            limit=limit
        )

        # 🔴 1) CACHE HIT → validar SIEMPRE
        cached_categories = self.cache.get(cache_key)
        if cached_categories:
            logger.debug(f"Cache HIT: {cache_key}")

            return [
                CategorySchema.model_validate(c)
                for c in cached_categories
            ]

        # 🟢 2) CACHE MISS → DB
        logger.debug(f"Cache MISS: {cache_key}")
        categories = super().get_all(skip, limit)

        # 🔒 3) FORZAR id (si no existe, explota acá)
        categories_schema: List[CategorySchema] = []

        for c in categories:
            if not hasattr(c, "id") or c.id is None:
                raise RuntimeError(
                    "Category sin id detectada. "
                    "El repository NO está trayendo la PK."
                )

            categories_schema.append(
                CategorySchema.model_validate(c)
            )

        # 💾 4) CACHEAR SOLO DATA CORRECTA
        categories_dict = [
            c.model_dump()
            for c in categories_schema
        ]

        self.cache.set(cache_key, categories_dict, ttl=self.cache_ttl)

        # ✅ 5) RESPUESTA FINAL (id garantizado)
        return categories_schema


    def get_one(self, id: int) -> CategorySchema:  # 👈 CAMBIAR id_key por id
        """Get single category by ID with caching"""
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id)

        cached_category = self.cache.get(cache_key)
        if cached_category is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return CategorySchema(**cached_category)

        logger.debug(f"Cache MISS: {cache_key}")
        category = super().get_one(id)  # 👈 CAMBIAR

        self.cache.set(cache_key, category.model_dump(), ttl=self.cache_ttl)

        return category

    def save(self, schema: CategorySchema) -> CategorySchema:
        """Create new category and invalidate cache"""
        category = super().save(schema)
        self._invalidate_all_cache()
        return category

    def update(self, id: int, schema: CategorySchema) -> CategorySchema:  # 👈 CAMBIAR
        """Update category with transactional cache invalidation"""
        try:
            category = super().update(id, schema)  # 👈 CAMBIAR
            self._invalidate_all_cache()
            logger.info(f"Category {id} updated and cache invalidated successfully")
            return category
        except Exception as e:
            logger.error(f"Failed to update category {id}: {e}")
            raise

    def delete(self, id: int) -> None:  # 👈 CAMBIAR
        """Delete category and invalidate cache"""
        super().delete(id)  # 👈 CAMBIAR
        self._invalidate_all_cache()

    def _invalidate_all_cache(self):
        """Invalidate all category caches"""
        pattern = f"{self.cache_prefix}:*"
        deleted_count = self.cache.delete_pattern(pattern)
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} category cache entries")