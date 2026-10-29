"""
Database ORM models package.

Importing all models here ensures they are registered with `Base.metadata`
for Alembic migrations and test schema creations.
"""

from app.db.base import Base
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product

__all__ = ["Base", "Customer", "Order", "OrderItem", "Product"]
