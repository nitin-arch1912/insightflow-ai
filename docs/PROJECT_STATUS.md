# InsightFlow AI — Project Status

> **Living document.** Update this file at the end of every milestone.
> The goal: anyone (including future-you after a break) can read this file
> and know exactly where the project stands and what to do next.

---

## Current State

| Field | Value |
|---|---|
| **Phase** | 3 — Database and Business Data |
| **Milestone** | Phase 3 Complete (Async SQLAlchemy 2.0, Alembic, Domain Models, Seed Data) |
| **Date** | 2026-10-29 |
| **Status** | ✅ Complete — 27/27 tests passing |

---

## Completed Features

### Phase 1 — Project Foundation
- [x] Git repository initialized (`main` branch)
- [x] Python virtual environment (`backend/.venv`)
- [x] FastAPI application skeleton (`backend/app/main.py`)
- [x] Environment-based configuration (`backend/app/core/config.py`)
- [x] Structured logging (`backend/app/core/logging.py`)
- [x] Health endpoint at `/health` and `/api/v1/health`
- [x] Root redirect to `/docs`
- [x] `.gitignore`, `.env.example`, README scaffold
- [x] Architecture decision record: ADR-001 (modular monolith)

### Phase 2 — Backend Foundations
- [x] `RequestIDMiddleware` for distributed request tracing via `X-Request-ID` header and context logging
- [x] RFC 7807 standardized JSON error handler (`code`, `message`, `details`, `request_id`)
- [x] Custom handlers for `StarletteHTTPException` (404, 405), `RequestValidationError` (422), and uncaught `Exception` (500)
- [x] Leak-safe 500 error responses (no internal stack traces exposed)
- [x] System metadata and uptime endpoint at `GET /api/v1/info`
- [x] API contract documented in `docs/api.md`

### Phase 3 — Database and Business Data
- [x] SQLAlchemy 2.0 async engine and session factory (`app/db/session.py`)
- [x] Dual-dialect support: SQLite async (`aiosqlite`) for zero-dependency local dev; PostgreSQL (`asyncpg`) for production
- [x] `docker-compose.yml` for local PostgreSQL 16 containerization
- [x] Core domain ORM models:
  - `Customer`: buyer profile, external ID, email, region
  - `Product`: catalog items, category, unit price, cost of goods sold
  - `Order`: financial transactions, status, order date, gross/discount/net amounts
  - `OrderItem`: line items, foreign keys, quantity checks
- [x] Alembic migration configuration and baseline revision (`0001_initial_schema.py`)
- [x] Database health check probe integrated into `GET /api/v1/health` (`"database": "connected"`)
- [x] Deterministic data seeder (`scripts/seed_data.py`) with 10 customers, 12 products, and 30 realistic orders
- [x] Sample CSV data files stored in `data/samples/`
- [x] 6 new database unit tests (27 total passing tests)

---

## Current Architecture

```
HTTP Request
    │
    ▼
FastAPI App (app/main.py)
    │
    ├── RequestIDMiddleware (app/core/middleware.py)
    ├── CORSMiddleware
    ├── Global Exception Handlers (app/core/exceptions.py)
    │
    ├─ /health              ← checks process & database connectivity (SELECT 1)
    ├─ /docs                ← OpenAPI UI
    └─ /api/v1/
        ├─ /health          ← versioned health check (includes DB status)
        └─ /info            ← system metadata & uptime
              │
              ▼
   SQLAlchemy 2.0 Async Session (app/db/session.py)
              │
              ▼
   Domain Models (app/models/): Customer, Product, Order, OrderItem
              │
              ▼
   Database: SQLite (local default) / PostgreSQL 16 (docker-compose)
```

---

## Dependencies

### Runtime (`requirements.txt`)
| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `pydantic` | Data validation and response models |
| `pydantic-settings` | Environment-based configuration |
| `python-dotenv` | Load `.env` file |
| `sqlalchemy` | SQL toolkit and ORM (2.0 async) |
| `alembic` | Database migrations |
| `asyncpg` | Async PostgreSQL driver |
| `aiosqlite` | Async SQLite driver (local dev fallback) |
| `greenlet` | Required for SQLAlchemy async operations |

### Dev (`requirements-dev.txt`)
| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `httpx` | Async HTTP client (TestClient dependency) |
| `pytest-asyncio` | Async test fixtures |

---

## Verified Tests

✅ **Verified 2026-10-29 — 27 passed, 0 failed, 1 warning (2.17s)**

```
pytest d:\ai_workspace\project\backend\tests\ -v
```

```
backend\tests\test_database.py::test_database_health_check PASSED        [  3%]
backend\tests\test_database.py::test_customers_seeded PASSED             [  7%]
backend\tests\test_database.py::test_products_seeded PASSED              [ 11%]
backend\tests\test_database.py::test_orders_and_relationships PASSED     [ 14%]
backend\tests\test_database.py::test_order_item_quantity_check_constraint PASSED [ 18%]
backend\tests\test_errors.py::test_404_error_format PASSED               [ 22%]
backend\tests\test_errors.py::test_405_error_format PASSED               [ 25%]
backend\tests\test_errors.py::test_422_validation_error_format PASSED    [ 29%]
backend\tests\test_errors.py::test_500_unhandled_exception_format PASSED [ 33%]
backend\tests\test_health.py::TestRootHealth::test_returns_200 PASSED    [ 37%]
backend\tests\test_health.py::TestRootHealth::test_status_is_ok PASSED   [ 40%]
backend\tests\test_health.py::TestRootHealth::test_version_is_present PASSED [ 44%]
backend\tests\test_api_v1_health::test_returns_200 PASSED                [ 48%]
backend\tests\test_api_v1_health::test_status_is_ok PASSED               [ 51%]
backend\tests\test_api_v1_health::test_version_matches_config PASSED     [ 55%]
backend\tests\test_api_v1_health::test_environment_is_present PASSED     [ 59%]
backend\tests\test_api_v1_health::test_database_is_connected PASSED     [ 62%]
backend\tests\test_api_v1_health::test_response_shape PASSED            [ 66%]
backend\tests\test_root_redirect::test_redirects_to_docs PASSED          [ 70%]
backend\tests\test_negative_cases::test_unknown_route_returns_404 PASSED [ 74%]
backend\tests\test_negative_cases::test_wrong_method_returns_405 PASSED  [ 77%]
backend\tests\test_info.py::test_get_system_info_returns_200 PASSED      [ 81%]
backend\tests\test_info.py::test_system_info_payload_structure PASSED    [ 85%]
backend\tests\test_info.py::test_system_info_includes_request_id_header PASSED [ 88%]
backend\tests\test_middleware.py::test_response_has_request_id_header PASSED [ 92%]
backend\tests\test_middleware.py::test_custom_request_id_is_preserved PASSED [ 96%]
backend\tests\test_middleware.py::test_sequential_requests_have_unique_ids PASSED [100%]

======================== 27 passed, 1 warning in 2.17s ========================
```

---

## Next Milestone

**Phase 4 — Business Analytics Core**
- Define deterministic business metrics: Total Revenue, Net Revenue, Total Orders, Average Order Value (AOV), Refund Rate, Customer Acquisition/Count.
- Implement tested SQL aggregation queries and analytics service layer (`app/services/analytics/`).
- Create typed response schemas for KPI summary, revenue trends over time, category breakdowns, and regional performance.
- Expose REST endpoints: `/api/v1/analytics/overview`, `/api/v1/analytics/trends`, `/api/v1/analytics/by-category`.
- Write unit tests verifying financial correctness against known ground truth data.
