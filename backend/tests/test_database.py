"""
Tests for the database layer, SQLAlchemy ORM models, relationships, and data integrity.

Verifies:
  - Database connectivity via async session
  - Seeded record counts (Customers, Products, Orders)
  - Relationship mapping (Customer -> Orders, Order -> OrderItems -> Product)
  - Business math consistency (net_amount == total_amount - discount_amount)
  - Database constraints (positive quantities)
"""

from decimal import Decimal
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db.session import async_session_factory, check_database_health
from app.models import Customer, Order, OrderItem, Product


@pytest.mark.asyncio
async def test_database_health_check() -> None:
    is_healthy = await check_database_health()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_customers_seeded() -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(func.count(Customer.id)))
        count = result.scalar()
        assert count == 10

        # Check unique regions exist
        region_res = await session.execute(select(Customer.region).distinct())
        regions = {row[0] for row in region_res.fetchall()}
        assert "North America" in regions
        assert "Europe" in regions
        assert "Asia-Pacific" in regions
        assert "Latin America" in regions


@pytest.mark.asyncio
async def test_products_seeded() -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(func.count(Product.id)))
        count = result.scalar()
        assert count == 12

        # Check categories
        cat_res = await session.execute(select(Product.category).distinct())
        categories = {row[0] for row in cat_res.fetchall()}
        assert categories == {"Electronics", "Office Supplies", "Furniture", "Software"}

        # Check all products have positive pricing and profit margin
        prod_res = await session.execute(select(Product))
        products = prod_res.scalars().all()
        for prod in products:
            assert prod.unit_price > Decimal("0.00")
            assert prod.cost_price > Decimal("0.00")
            assert prod.unit_price > prod.cost_price, f"{prod.name} should have a positive markup"


@pytest.mark.asyncio
async def test_orders_and_relationships() -> None:
    async with async_session_factory() as session:
        # Load orders with customer and items eagerly
        stmt = (
            select(Order)
            .options(selectinload(Order.customer), selectinload(Order.items).selectinload(OrderItem.product))
            .limit(10)
        )
        result = await session.execute(stmt)
        orders = result.scalars().all()

        assert len(orders) > 0
        for order in orders:
            assert order.customer is not None
            assert len(order.items) > 0

            # Verify line item totals sum to gross total_amount
            sum_line_items = sum((item.total_price for item in order.items), Decimal("0.00"))
            assert order.total_amount == sum_line_items

            # Verify net amount calculation: net = total - discount
            expected_net = max(Decimal("0.00"), order.total_amount - order.discount_amount)
            assert order.net_amount == expected_net

            # Each item links to a valid product
            for item in order.items:
                assert item.product is not None
                assert item.quantity > 0
                assert item.total_price == item.unit_price * item.quantity


@pytest.mark.asyncio
async def test_order_item_quantity_check_constraint() -> None:
    """Verifies that the database rejects invalid line items (quantity <= 0)."""
    async with async_session_factory() as session:
        # Fetch an existing order and product
        order_res = await session.execute(select(Order).limit(1))
        order = order_res.scalar_one()

        prod_res = await session.execute(select(Product).limit(1))
        product = prod_res.scalar_one()

        invalid_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=0,  # Violates chk_order_item_quantity_positive
            unit_price=product.unit_price,
            total_price=Decimal("0.00"),
        )
        session.add(invalid_item)

        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()
