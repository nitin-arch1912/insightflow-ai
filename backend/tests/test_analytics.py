"""
Unit and integration tests for analytics service and REST endpoints.

Verifies mathematical correctness of business calculations against the
known seeded ground-truth dataset:
  - 30 total orders (26 completed, 2 pending, 1 refunded, 1 cancelled)
  - Gross completed revenue: $47,535.38
  - Discounts given: $915.00
  - Net completed revenue: $46,620.38
  - AOV: $1,793.09
  - Refund rate: 3.33% (1/30)
  - Active customers: 10
"""

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app, raise_server_exceptions=True)


# ------------------------------------------------------------------ #
# 1. Overview Analytics Tests                                         #
# ------------------------------------------------------------------ #

def test_overview_unfiltered_metrics(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()

    assert Decimal(str(data["gross_revenue"])) == Decimal("47535.38")
    assert Decimal(str(data["discount_amount"])) == Decimal("915.00")
    assert Decimal(str(data["net_revenue"])) == Decimal("46620.38")
    assert data["total_orders"] == 30
    assert data["completed_orders"] == 26
    assert Decimal(str(data["average_order_value"])) == Decimal("1793.09")
    assert data["refund_rate_percentage"] == 3.33
    assert data["active_customers"] == 10


def test_overview_filter_by_region(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/overview?region=North%20America")
    assert response.status_code == 200
    data = response.json()

    # Region-specific numbers must be less than global totals
    assert Decimal(str(data["net_revenue"])) < Decimal("46620.38")
    assert data["total_orders"] < 30
    assert data["active_customers"] <= 3  # Acme, Global Retail, Apex


def test_overview_empty_date_range_handles_division_by_zero(client: TestClient) -> None:
    # Query future date range with 0 orders
    response = client.get("/api/v1/analytics/overview?start_date=2030-01-01T00:00:00Z&end_date=2030-01-31T23:59:59Z")
    assert response.status_code == 200
    data = response.json()

    assert Decimal(str(data["gross_revenue"])) == Decimal("0.00")
    assert Decimal(str(data["net_revenue"])) == Decimal("0.00")
    assert data["total_orders"] == 0
    assert data["completed_orders"] == 0
    assert Decimal(str(data["average_order_value"])) == Decimal("0.00")
    assert data["refund_rate_percentage"] == 0.0


# ------------------------------------------------------------------ #
# 2. Category Breakdown Tests                                         #
# ------------------------------------------------------------------ #

def test_category_breakdown(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/by-category")
    assert response.status_code == 200
    data = response.json()

    items = data["items"]
    assert len(items) == 4

    categories = {item["category"] for item in items}
    assert categories == {"Electronics", "Software", "Furniture", "Office Supplies"}

    # Verify percentages sum approximately to 100%
    total_pct = sum(item["percentage_of_total"] for item in items)
    assert 99.0 <= total_pct <= 101.0

    # Verify sorted descending by revenue
    revenues = [Decimal(str(item["revenue"])) for item in items]
    assert revenues == sorted(revenues, reverse=True)


# ------------------------------------------------------------------ #
# 3. Region Breakdown Tests                                           #
# ------------------------------------------------------------------ #

def test_region_breakdown(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/by-region")
    assert response.status_code == 200
    data = response.json()

    items = data["items"]
    assert len(items) == 4

    regions = {item["region"] for item in items}
    assert regions == {"North America", "Europe", "Asia-Pacific", "Latin America"}

    # Ensure all regions generated positive completed revenue
    for item in items:
        assert Decimal(str(item["revenue"])) > Decimal("0.00")
        assert item["order_count"] > 0
        assert item["customer_count"] > 0


# ------------------------------------------------------------------ #
# 4. Trends Tests                                                     #
# ------------------------------------------------------------------ #

def test_trends_daily(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/trends?interval=daily")
    assert response.status_code == 200
    data = response.json()

    assert data["interval"] == "daily"
    items = data["items"]
    assert len(items) > 0

    # Ensure chronological ordering
    dates = [item["date"] for item in items]
    assert dates == sorted(dates)

    for item in items:
        assert "date" in item
        assert Decimal(str(item["gross_revenue"])) >= Decimal("0.00")
        assert Decimal(str(item["net_revenue"])) >= Decimal("0.00")
        assert item["order_count"] > 0
