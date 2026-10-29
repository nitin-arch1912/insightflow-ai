"""
Pydantic schemas for analytics query responses and filters.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TrendInterval(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


# ------------------------------------------------------------------ #
# KPI Overview                                                         #
# ------------------------------------------------------------------ #

class AnalyticsOverviewResponse(BaseModel):
    gross_revenue: Decimal = Field(..., description="Sum of total amount for completed orders")
    discount_amount: Decimal = Field(..., description="Sum of discounts applied to completed orders")
    net_revenue: Decimal = Field(..., description="Gross revenue minus discounts for completed orders")
    total_orders: int = Field(..., description="Total count of all placed orders (all statuses)")
    completed_orders: int = Field(..., description="Count of completed orders")
    average_order_value: Decimal = Field(..., description="Net revenue divided by completed orders")
    refund_rate_percentage: float = Field(..., description="Percentage of placed orders that were refunded")
    active_customers: int = Field(..., description="Count of distinct customers who placed completed orders")

    model_config = {
        "json_schema_extra": {
            "example": {
                "gross_revenue": "47535.38",
                "discount_amount": "915.00",
                "net_revenue": "46620.38",
                "total_orders": 30,
                "completed_orders": 26,
                "average_order_value": "1793.09",
                "refund_rate_percentage": 3.33,
                "active_customers": 10,
            }
        }
    }


# ------------------------------------------------------------------ #
# Category Breakdown                                                   #
# ------------------------------------------------------------------ #

class CategoryBreakdownItem(BaseModel):
    category: str
    revenue: Decimal
    units_sold: int
    order_count: int
    percentage_of_total: float


class CategoryBreakdownResponse(BaseModel):
    items: list[CategoryBreakdownItem]
    total_category_revenue: Decimal


# ------------------------------------------------------------------ #
# Regional Breakdown                                                   #
# ------------------------------------------------------------------ #

class RegionBreakdownItem(BaseModel):
    region: str
    revenue: Decimal
    order_count: int
    customer_count: int


class RegionBreakdownResponse(BaseModel):
    items: list[RegionBreakdownItem]
    total_regional_revenue: Decimal


# ------------------------------------------------------------------ #
# Trends                                                               #
# ------------------------------------------------------------------ #

class TrendItem(BaseModel):
    date: str
    gross_revenue: Decimal
    net_revenue: Decimal
    order_count: int


class TrendResponse(BaseModel):
    interval: TrendInterval
    items: list[TrendItem]
