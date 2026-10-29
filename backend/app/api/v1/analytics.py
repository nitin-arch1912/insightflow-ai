"""
Analytics API endpoints — /api/v1/analytics/*

Exposes deterministic business metrics for dashboards, visualizations,
and the natural-language analytics engine.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CategoryBreakdownResponse,
    RegionBreakdownResponse,
    TrendInterval,
    TrendResponse,
)
from app.services.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get business overview KPIs",
    description="Returns aggregate KPI metrics: gross/net revenue, order volume, AOV, refund rate, active customers.",
)
async def get_analytics_overview(
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    region: Optional[str] = Query(None, description="Filter by customer geographic region"),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsOverviewResponse:
    service = AnalyticsService(db)
    return await service.get_overview(start_date=start_date, end_date=end_date, region=region)


@router.get(
    "/by-category",
    response_model=CategoryBreakdownResponse,
    summary="Get revenue by product category",
    description="Returns completed revenue, units sold, order count, and revenue share by product category.",
)
async def get_analytics_by_category(
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    db: AsyncSession = Depends(get_db),
) -> CategoryBreakdownResponse:
    service = AnalyticsService(db)
    return await service.get_category_breakdown(start_date=start_date, end_date=end_date)


@router.get(
    "/by-region",
    response_model=RegionBreakdownResponse,
    summary="Get revenue by customer region",
    description="Returns completed net revenue, order count, and active customers by region.",
)
async def get_analytics_by_region(
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    db: AsyncSession = Depends(get_db),
) -> RegionBreakdownResponse:
    service = AnalyticsService(db)
    return await service.get_region_breakdown(start_date=start_date, end_date=end_date)


@router.get(
    "/trends",
    response_model=TrendResponse,
    summary="Get time-series revenue trends",
    description="Returns periodic time-series revenue metrics suitable for charting.",
)
async def get_analytics_trends(
    interval: TrendInterval = Query(TrendInterval.DAILY, description="Grouping period"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    db: AsyncSession = Depends(get_db),
) -> TrendResponse:
    service = AnalyticsService(db)
    return await service.get_trends(interval=interval, start_date=start_date, end_date=end_date)
