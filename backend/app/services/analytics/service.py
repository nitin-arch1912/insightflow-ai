"""
Analytics business service layer.

Executes deterministic SQL aggregation queries to calculate authoritative
business performance metrics (revenue, order volume, AOV, refunds, breakdowns).

All mathematical formulas and rules are codified in Python/SQL:
  - Gross Revenue = SUM(total_amount) for completed orders
  - Discounts = SUM(discount_amount) for completed orders
  - Net Revenue = SUM(net_amount) for completed orders
  - Average Order Value (AOV) = Net Revenue / Completed Orders
  - Refund Rate = (Refunded Orders Count / Total Placed Orders) * 100
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer, Order, OrderItem, Product
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CategoryBreakdownItem,
    CategoryBreakdownResponse,
    RegionBreakdownItem,
    RegionBreakdownResponse,
    TrendInterval,
    TrendItem,
    TrendResponse,
)


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_overview(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        region: Optional[str] = None,
    ) -> AnalyticsOverviewResponse:
        """Calculate high-level KPI card metrics."""
        # 1. Total placed orders and refunded orders query
        order_filter = []
        if start_date:
            order_filter.append(Order.order_date >= start_date)
        if end_date:
            order_filter.append(Order.order_date <= end_date)

        total_orders_query = select(
            func.count(Order.id).label("total_orders"),
            func.count(Order.id).filter(Order.status == "refunded").label("refunded_orders"),
        )
        if region:
            total_orders_query = total_orders_query.join(Customer).where(Customer.region == region)
        if order_filter:
            total_orders_query = total_orders_query.where(*order_filter)

        total_res = await self.session.execute(total_orders_query)
        total_row = total_res.first()
        total_orders = total_row.total_orders or 0
        refunded_orders = total_row.refunded_orders or 0

        # 2. Completed orders financial totals
        completed_filter = [*order_filter, Order.status == "completed"]
        financial_query = select(
            func.coalesce(func.sum(Order.total_amount), Decimal("0.00")).label("gross_revenue"),
            func.coalesce(func.sum(Order.discount_amount), Decimal("0.00")).label("discount_amount"),
            func.coalesce(func.sum(Order.net_amount), Decimal("0.00")).label("net_revenue"),
            func.count(Order.id).label("completed_orders"),
            func.count(func.distinct(Order.customer_id)).label("active_customers"),
        )
        if region:
            financial_query = financial_query.join(Customer).where(Customer.region == region)
        financial_query = financial_query.where(*completed_filter)

        fin_res = await self.session.execute(financial_query)
        fin_row = fin_res.first()

        gross_rev = Decimal(str(fin_row.gross_revenue))
        disc_amt = Decimal(str(fin_row.discount_amount))
        net_rev = Decimal(str(fin_row.net_revenue))
        completed_orders = fin_row.completed_orders or 0
        active_customers = fin_row.active_customers or 0

        aov = round(net_rev / completed_orders, 2) if completed_orders > 0 else Decimal("0.00")
        refund_rate = round((refunded_orders / total_orders) * 100, 2) if total_orders > 0 else 0.0

        return AnalyticsOverviewResponse(
            gross_revenue=gross_rev,
            discount_amount=disc_amt,
            net_revenue=net_rev,
            total_orders=total_orders,
            completed_orders=completed_orders,
            average_order_value=aov,
            refund_rate_percentage=refund_rate,
            active_customers=active_customers,
        )

    async def get_category_breakdown(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> CategoryBreakdownResponse:
        """Calculate sales volume and revenue grouped by product category."""
        filters = [Order.status == "completed"]
        if start_date:
            filters.append(Order.order_date >= start_date)
        if end_date:
            filters.append(Order.order_date <= end_date)

        query = (
            select(
                Product.category.label("category"),
                func.sum(OrderItem.total_price).label("revenue"),
                func.sum(OrderItem.quantity).label("units_sold"),
                func.count(func.distinct(OrderItem.order_id)).label("order_count"),
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .where(*filters)
            .group_by(Product.category)
            .order_by(func.sum(OrderItem.total_price).desc())
        )

        res = await self.session.execute(query)
        rows = res.all()

        total_cat_rev = sum((Decimal(str(r.revenue)) for r in rows), Decimal("0.00"))

        items = []
        for r in rows:
            rev = Decimal(str(r.revenue))
            pct = round(float((rev / total_cat_rev) * 100), 2) if total_cat_rev > 0 else 0.0
            items.append(
                CategoryBreakdownItem(
                    category=r.category,
                    revenue=rev,
                    units_sold=r.units_sold,
                    order_count=r.order_count,
                    percentage_of_total=pct,
                )
            )

        return CategoryBreakdownResponse(
            items=items,
            total_category_revenue=total_cat_rev,
        )

    async def get_region_breakdown(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RegionBreakdownResponse:
        """Calculate net sales revenue and customer counts by geographic region."""
        filters = [Order.status == "completed"]
        if start_date:
            filters.append(Order.order_date >= start_date)
        if end_date:
            filters.append(Order.order_date <= end_date)

        query = (
            select(
                Customer.region.label("region"),
                func.sum(Order.net_amount).label("revenue"),
                func.count(Order.id).label("order_count"),
                func.count(func.distinct(Customer.id)).label("customer_count"),
            )
            .join(Order, Customer.id == Order.customer_id)
            .where(*filters)
            .group_by(Customer.region)
            .order_by(func.sum(Order.net_amount).desc())
        )

        res = await self.session.execute(query)
        rows = res.all()

        total_regional_rev = sum((Decimal(str(r.revenue)) for r in rows), Decimal("0.00"))

        items = [
            RegionBreakdownItem(
                region=r.region,
                revenue=Decimal(str(r.revenue)),
                order_count=r.order_count,
                customer_count=r.customer_count,
            )
            for r in rows
        ]

        return RegionBreakdownResponse(
            items=items,
            total_regional_revenue=total_regional_rev,
        )

    async def get_trends(
        self,
        interval: TrendInterval = TrendInterval.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> TrendResponse:
        """Calculate revenue time-series trends."""
        filters = [Order.status == "completed"]
        if start_date:
            filters.append(Order.order_date >= start_date)
        if end_date:
            filters.append(Order.order_date <= end_date)

        date_col = func.date(Order.order_date).label("period")

        query = (
            select(
                date_col,
                func.sum(Order.total_amount).label("gross_revenue"),
                func.sum(Order.net_amount).label("net_revenue"),
                func.count(Order.id).label("order_count"),
            )
            .where(*filters)
            .group_by(date_col)
            .order_by(date_col.asc())
        )

        res = await self.session.execute(query)
        rows = res.all()

        items = [
            TrendItem(
                date=str(r.period),
                gross_revenue=Decimal(str(r.gross_revenue)),
                net_revenue=Decimal(str(r.net_revenue)),
                order_count=r.order_count,
            )
            for r in rows
        ]

        return TrendResponse(
            interval=interval,
            items=items,
        )
