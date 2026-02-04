"""Product service with Redis caching integration and sanitized logging."""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from cloudinary.uploader import upload

from models.product import ProductModel
from repositories.product_repository import ProductRepository
from schemas.product_schema import ProductSchema
from services.base_service_impl import BaseServiceImpl
from services.cache_service import cache_service
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)  # P11: Sanitized logging


class ProductService(BaseServiceImpl):
    """Service for Product entity with caching."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=ProductRepository,
            model=ProductModel,
            schema=ProductSchema,
            db=db
        )
        self.cache = cache_service
        self.cache_prefix = "products"

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ProductSchema]:
        """
        Get all products with caching

        Cache key pattern: products:list:skip:{skip}:limit:{limit}
        TTL: 5 minutes (default REDIS_CACHE_TTL)
        """
        # Build cache key
        cache_key = self.cache.build_key(
            self.cache_prefix,
            "list",
            skip=skip,
            limit=limit
        )

        # Try to get from cache
        cached_products = self.cache.get(cache_key)
        if cached_products is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            # Convert dict list back to ProductSchema list
            return [ProductSchema(**p) for p in cached_products]

        # Cache miss - get from database
        logger.debug(f"Cache MISS: {cache_key}")
        products = super().get_all(skip, limit)

        # Cache the result (convert to dict for JSON serialization)
        products_dict = [p.model_dump() for p in products]
        self.cache.set(cache_key, products_dict)

        return products

    def get_one(self, id_key: int) -> ProductSchema:
        """
        Get single product by ID with caching

        Cache key pattern: products:id:{id_key}
        TTL: 5 minutes
        """
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        # Try cache first
        cached_product = self.cache.get(cache_key)
        if cached_product is not None:
            logger.debug(f"Cache HIT: {cache_key}")
            return ProductSchema(**cached_product)

        # Get from database
        logger.debug(f"Cache MISS: {cache_key}")
        product = super().get_one(id_key)

        # Cache the result
        self.cache.set(cache_key, product.model_dump())

        return product

    def save(self, schema: ProductSchema, image_file=None) -> ProductSchema:
        """
        Create new product, upload image to Cloudinary if provided,
        persist product, and invalidate cache.
        """

        # 1️⃣ Subida de imagen (si existe)
        if image_file:
            # Asegura que el stream esté al inicio
            image_file.file.seek(0)

            upload_result = upload(
                image_file.file,
                folder="products",
                resource_type="image"
            )

            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", upload_result)

            # SOLO strings en el schema
            schema.image_url = upload_result["secure_url"]
            schema.image_public_id = upload_result["public_id"]

        # 2️⃣ Guardado en DB (esto suele devolver un modelo SQLAlchemy)
        db_product = super().save(schema)

        # 3️⃣ Conversión EXPLÍCITA a schema limpio (clave del fix)
        # Evita que FastAPI intente serializar cosas raras
        if isinstance(db_product, ProductSchema):
            result = db_product
        else:
            result = ProductSchema.model_validate(db_product)

        # 4️⃣ Invalidar cache
        self._invalidate_list_cache()

        return result

    def update(self, id_key: int, schema: ProductSchema) -> ProductSchema:
        """
        Update product with transactional cache invalidation

        Args:
            id_key: Product ID to update
            schema: Validated ProductSchema with new data

        Returns:
            Updated product schema

        Raises:
            InstanceNotFoundError: If product doesn't exist
            ValueError: If validation fails
        """
        # Build cache keys BEFORE update (prepare for invalidation)
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        try:
            # Update in database (atomic transaction)
            product = super().update(id_key, schema)

            # Only invalidate cache AFTER successful DB commit
            self.cache.delete(cache_key)
            self._invalidate_list_cache()

            logger.info(f"Product {id_key} updated and cache invalidated successfully")
            return product

        except Exception as e:
            # If update fails, cache remains consistent (no invalidation)
            logger.error(f"Failed to update product {id_key}: {e}")
            raise

    def delete(self, id_key: int) -> None:
        """
        Delete product with validation to prevent loss of sales history

        Raises:
            ValueError: If product has associated order details (sales history)
            InstanceNotFoundError: If product doesn't exist
        """
        from models.order_detail import OrderDetailModel
        from sqlalchemy import select

        # Check if product has sales history
        stmt = select(OrderDetailModel).where(
            OrderDetailModel.product_id == id_key
        ).limit(1)

        # Get session from repository
        has_sales = self._repository.session.scalars(stmt).first()

        if has_sales:
            logger.error(
                f"Cannot delete product {id_key}: has associated sales history"
            )
            raise ValueError(
                f"Cannot delete product {id_key}: product has associated sales history. "
                f"Consider marking as inactive instead of deleting."
            )

        # Safe to delete
        logger.info(f"Deleting product {id_key} (no sales history)")
        super().delete(id_key)

        # Invalidate specific product cache
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)
        self.cache.delete(cache_key)

        # Invalidate list cache
        self._invalidate_list_cache()

    def _invalidate_list_cache(self):
        """Invalidate all product list caches"""
        pattern = f"{self.cache_prefix}:list:*"
        deleted_count = self.cache.delete_pattern(pattern)
        if deleted_count > 0:
            logger.info(f"Invalidated {deleted_count} product list cache entries")
