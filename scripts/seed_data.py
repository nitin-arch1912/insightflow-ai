"""
Deterministic business data seeder for InsightFlow AI.

Populates the database with realistic e-commerce/retail sample data:
  - 10 Customers across 4 global regions
  - 12 Products across 4 merchandise categories
  - 30 Orders with realistic line items, discounts, statuses, and timestamps

Idempotent: Clears previously seeded sample records before re-inserting.

Run:
    python scripts/seed_data.py
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure backend package is discoverable
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.session import async_session_factory
from app.models import Customer, Order, OrderItem, Product


# ------------------------------------------------------------------ #
# Seed Datasets                                                        #
# ------------------------------------------------------------------ #

SAMPLE_CUSTOMERS = [
    {"external_id": "CUST-1001", "name": "Acme Industrial Corp", "email": "procurement@acmeind.com", "region": "North America"},
    {"external_id": "CUST-1002", "name": "Global Retail Partners", "email": "ops@globalretail.com", "region": "North America"},
    {"external_id": "CUST-1003", "name": "Nordic Solutions AB", "email": "contact@nordicsolutions.se", "region": "Europe"},
    {"external_id": "CUST-1004", "name": "Bavaria Logistics GmbH", "email": "supply@bavaria-log.de", "region": "Europe"},
    {"external_id": "CUST-1005", "name": "Pacific Rim Technologies", "email": "buyer@pacificrimtech.jp", "region": "Asia-Pacific"},
    {"external_id": "CUST-1006", "name": "Singapore Analytics Pte", "email": "admin@sg-analytics.sg", "region": "Asia-Pacific"},
    {"external_id": "CUST-1007", "name": "Sao Paulo Trading S.A.", "email": "compras@sptrading.br", "region": "Latin America"},
    {"external_id": "CUST-1008", "name": "Andes Mining & Tech", "email": "operations@andesmining.cl", "region": "Latin America"},
    {"external_id": "CUST-1009", "name": "Apex Cloud Systems", "email": "finance@apexcloud.io", "region": "North America"},
    {"external_id": "CUST-1010", "name": "London Fintech Ventures", "email": "it@londonfintech.co.uk", "region": "Europe"},
]

SAMPLE_PRODUCTS = [
    # Electronics
    {"sku": "PROD-EL-001", "name": "UltraBook Pro 15", "category": "Electronics", "unit_price": Decimal("1299.99"), "cost_price": Decimal("850.00")},
    {"sku": "PROD-EL-002", "name": "4K UHD 27-inch Monitor", "category": "Electronics", "unit_price": Decimal("389.50"), "cost_price": Decimal("220.00")},
    {"sku": "PROD-EL-003", "name": "Wireless Noise-Canceling Headset", "category": "Electronics", "unit_price": Decimal("179.99"), "cost_price": Decimal("85.00")},
    
    # Office Supplies
    {"sku": "PROD-OF-001", "name": "Ergonomic Mechanical Keyboard", "category": "Office Supplies", "unit_price": Decimal("119.00"), "cost_price": Decimal("55.00")},
    {"sku": "PROD-OF-002", "name": "Precision Laser Mouse", "category": "Office Supplies", "unit_price": Decimal("59.90"), "cost_price": Decimal("25.00")},
    {"sku": "PROD-OF-003", "name": "Recycled Paper Carton (10 reams)", "category": "Office Supplies", "unit_price": Decimal("44.50"), "cost_price": Decimal("22.00")},

    # Furniture
    {"sku": "PROD-FN-001", "name": "Executive Mesh Task Chair", "category": "Furniture", "unit_price": Decimal("349.00"), "cost_price": Decimal("160.00")},
    {"sku": "PROD-FN-002", "name": "Motorized Standing Desk 60x30", "category": "Furniture", "unit_price": Decimal("599.00"), "cost_price": Decimal("320.00")},
    {"sku": "PROD-FN-003", "name": "Acoustic Desk Privacy Panel", "category": "Furniture", "unit_price": Decimal("129.00"), "cost_price": Decimal("50.00")},

    # Software
    {"sku": "PROD-SW-001", "name": "InsightFlow Analytics License (Annual)", "category": "Software", "unit_price": Decimal("999.00"), "cost_price": Decimal("120.00")},
    {"sku": "PROD-SW-002", "name": "Security & Backup Suite (Annual)", "category": "Software", "unit_price": Decimal("499.00"), "cost_price": Decimal("80.00")},
    {"sku": "PROD-SW-003", "name": "Cloud Collaboration Hub (Annual)", "category": "Software", "unit_price": Decimal("299.00"), "cost_price": Decimal("40.00")},
]


async def seed() -> None:
    print("[INFO] Starting database seeding...")
    base_date = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)

    async with async_session_factory() as session:
        # 1. Clean existing records in reverse dependency order
        print("  - Clearing existing records...")
        await session.execute(delete(OrderItem))
        await session.execute(delete(Order))
        await session.execute(delete(Customer))
        await session.execute(delete(Product))
        await session.commit()

        # 2. Insert Customers
        print("  - Inserting customers...")
        customer_objs = [Customer(**data) for data in SAMPLE_CUSTOMERS]
        session.add_all(customer_objs)
        await session.flush()

        # 3. Insert Products
        print("  - Inserting products...")
        product_objs = [Product(**data) for data in SAMPLE_PRODUCTS]
        session.add_all(product_objs)
        await session.flush()

        # Map by index for consistent order generation
        customers = customer_objs
        products = product_objs

        # 4. Generate 30 realistic orders with items
        print("  - Generating orders and line items...")
        order_specs = [
            (0, 28, "completed", Decimal("50.00"), [(0, 2), (3, 2)]), # Acme: 2 Laptops, 2 Keyboards
            (1, 27, "completed", Decimal("0.00"),  [(6, 4), (7, 2)]), # Global Retail: 4 Chairs, 2 Desks
            (2, 26, "completed", Decimal("100.00"),[(9, 1), (10, 1)]),# Nordic: 1 Analytics, 1 Security
            (3, 25, "refunded",  Decimal("0.00"),  [(1, 3)]),          # Bavaria: 3 Monitors (refunded)
            (4, 24, "completed", Decimal("25.00"), [(2, 5), (4, 5)]), # Pacific Rim: 5 Headsets, 5 Mice
            (5, 23, "completed", Decimal("0.00"),  [(0, 1), (9, 1)]), # Singapore: 1 Laptop, 1 Analytics
            (6, 22, "completed", Decimal("15.00"), [(5, 10)]),         # Sao Paulo: 10 Paper Cartons
            (7, 21, "pending",   Decimal("0.00"),  [(7, 1), (6, 1)]), # Andes: 1 Desk, 1 Chair
            (8, 20, "completed", Decimal("200.00"),[(0, 5), (1, 5)]), # Apex: 5 Laptops, 5 Monitors
            (9, 19, "completed", Decimal("0.00"),  [(10, 2), (11, 2)]),# London Fintech: 2 Security, 2 Collab
            (0, 18, "completed", Decimal("0.00"),  [(2, 2), (4, 2)]), # Acme: 2 Headsets, 2 Mice
            (1, 17, "cancelled", Decimal("0.00"),  [(0, 1)]),          # Global Retail: Cancelled Laptop
            (2, 16, "completed", Decimal("30.00"), [(1, 2), (3, 2)]), # Nordic: 2 Monitors, 2 Keyboards
            (3, 15, "completed", Decimal("0.00"),  [(6, 2)]),          # Bavaria: 2 Chairs
            (4, 14, "completed", Decimal("50.00"), [(7, 3), (8, 3)]), # Pacific Rim: 3 Desks, 3 Panels
            (5, 13, "completed", Decimal("0.00"),  [(9, 2)]),          # Singapore: 2 Analytics Licenses
            (6, 12, "completed", Decimal("0.00"),  [(3, 4), (4, 4)]), # Sao Paulo: 4 Keyboards, 4 Mice
            (7, 11, "completed", Decimal("75.00"), [(0, 3)]),          # Andes: 3 Laptops
            (8, 10, "completed", Decimal("0.00"),  [(1, 4), (2, 4)]), # Apex: 4 Monitors, 4 Headsets
            (9, 9,  "completed", Decimal("120.00"),[(9, 1), (6, 2)]), # London Fintech: 1 Analytics, 2 Chairs
            (0, 8,  "completed", Decimal("0.00"),  [(5, 5)]),          # Acme: 5 Paper Cartons
            (1, 7,  "completed", Decimal("40.00"), [(0, 1), (1, 1)]), # Global Retail: 1 Laptop, 1 Monitor
            (2, 6,  "pending",   Decimal("0.00"),  [(7, 2)]),          # Nordic: 2 Desks
            (3, 5,  "completed", Decimal("10.00"), [(2, 3)]),          # Bavaria: 3 Headsets
            (4, 4,  "completed", Decimal("0.00"),  [(11, 3)]),         # Pacific Rim: 3 Collab Suites
            (5, 3,  "completed", Decimal("50.00"), [(0, 2), (7, 1)]), # Singapore: 2 Laptops, 1 Desk
            (6, 2,  "completed", Decimal("0.00"),  [(1, 1), (3, 1)]), # Sao Paulo: 1 Monitor, 1 Keyboard
            (7, 1,  "completed", Decimal("0.00"),  [(8, 4)]),          # Andes: 4 Acoustic Panels
            (8, 0,  "completed", Decimal("150.00"),[(0, 2), (9, 1)]), # Apex: 2 Laptops, 1 Analytics
            (9, 0,  "completed", Decimal("0.00"),  [(2, 2), (4, 2)]), # London Fintech: 2 Headsets, 2 Mice
        ]

        for i, (c_idx, days_ago, status, discount, items_spec) in enumerate(order_specs, start=1):
            order_date = base_date + timedelta(days=28 - days_ago, hours=i % 8)
            order_num = f"ORD-2026-{1000 + i}"

            gross_total = Decimal("0.00")
            item_objs = []

            for p_idx, qty in items_spec:
                prod = products[p_idx]
                line_total = prod.unit_price * qty
                gross_total += line_total

                item_objs.append(
                    OrderItem(
                        product_id=prod.id,
                        quantity=qty,
                        unit_price=prod.unit_price,
                        total_price=line_total,
                    )
                )

            net_total = max(Decimal("0.00"), gross_total - discount)

            order = Order(
                order_number=order_num,
                customer_id=customers[c_idx].id,
                status=status,
                order_date=order_date,
                total_amount=gross_total,
                discount_amount=discount,
                net_amount=net_total,
                items=item_objs,
            )
            session.add(order)

        await session.commit()
        print("[SUCCESS] Database successfully seeded with 10 customers, 12 products, and 30 orders!")


if __name__ == "__main__":
    asyncio.run(seed())
