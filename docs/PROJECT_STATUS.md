# InsightFlow AI — Project Status

> **Living document.** Update this file at the end of every milestone.
> The goal: anyone (including future-you after a break) can read this file
> and know exactly where the project stands and what to do next.

---

## Current State

| Field | Value |
|---|---|
| **Phase** | 2 — Backend Foundations |
| **Milestone** | Phase 2 Complete (Request ID, RFC 7807 Error Handling, System Info) |
| **Date** | 2026-10-29 |
| **Status** | ✅ Complete — 21/21 tests passing |

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
- [x] Comprehensive test coverage across middleware, errors, and system info
- [x] API contract documented in `docs/api.md`

---

## Current Architecture

```
HTTP Request
    │
    ▼
FastAPI App (app/main.py)
    │
    ├── RequestIDMiddleware (app/core/middleware.py)  [attaches X-Request-ID & logs request]
    ├── CORSMiddleware
    ├── Global Exception Handlers (app/core/exceptions.py) [uniform RFC 7807 JSON errors]
    │
    ├─ /health              ← bare health check
    ├─ /docs                ← OpenAPI UI (auto-generated)
    └─ /api/v1/
        ├─ /health          ← versioned health check (app/api/v1/health.py)
        └─ /info            ← system metadata & uptime (app/api/v1/info.py)
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

### Dev (`requirements-dev.txt`)
| Package | Purpose |
|---|---|
| `pytest` | Test runner |
| `httpx` | Async HTTP client (TestClient dependency) |
| `pytest-asyncio` | Async test fixtures |

---

## Verified Tests

✅ **Verified 2026-10-29 — 21 passed, 0 failed, 1 warning (1.58s)**

```
pytest d:\ai_workspace\project\backend\tests\ -v
```

```
backend\tests\test_errors.py::test_404_error_format PASSED               [  4%]
backend\tests\test_errors.py::test_405_error_format PASSED               [  9%]
backend\tests\test_errors.py::test_422_validation_error_format PASSED    [ 14%]
backend\tests\test_errors.py::test_500_unhandled_exception_format PASSED [ 19%]
backend\tests\test_health.py::TestRootHealth::test_returns_200 PASSED    [ 23%]
backend\tests\test_health.py::TestRootHealth::test_status_is_ok PASSED   [ 28%]
backend\tests\test_health.py::TestRootHealth::test_version_is_present PASSED [ 33%]
backend\tests\test_health.py::TestApiV1Health::test_returns_200 PASSED   [ 38%]
backend\tests\test_health.py::TestApiV1Health::test_status_is_ok PASSED  [ 42%]
backend\tests\test_health.py::TestApiV1Health::test_version_matches_config PASSED [ 47%]
backend\tests\test_health.py::TestApiV1Health::test_environment_is_present PASSED [ 52%]
backend\tests\test_health.py::TestApiV1Health::test_response_shape PASSED [ 57%]
backend\tests\test_health.py::TestRootRedirect::test_redirects_to_docs PASSED [ 61%]
backend\tests\test_health.py::TestNegativeCases::test_unknown_route_returns_404 PASSED [ 66%]
backend\tests\test_health.py::TestNegativeCases::test_wrong_method_returns_405 PASSED [ 71%]
backend\tests\test_info.py::test_get_system_info_returns_200 PASSED      [ 76%]
backend\tests\test_info.py::test_system_info_payload_structure PASSED    [ 80%]
backend\tests\test_info.py::test_system_info_includes_request_id_header PASSED [ 85%]
backend\tests\test_middleware.py::test_response_has_request_id_header PASSED [ 90%]
backend\tests\test_middleware.py::test_custom_request_id_is_preserved PASSED [ 95%]
backend\tests\test_middleware.py::test_sequential_requests_have_unique_ids PASSED [100%]

======================== 21 passed, 1 warning in 1.58s ========================
```

---

## Known Issues & Notes

- Docker Desktop is not yet installed (required for Phase 3 PostgreSQL).
- Database layer has not yet been introduced.
- Deprecation warning in starlette testclient with httpx (non-blocking).

---

## Next Milestone

**Phase 3 — Database and Business Data**
- Configure PostgreSQL connection (async SQLAlchemy 2.0).
- Initialize Alembic migration environment.
- Define core domain models: `Customer`, `Product`, `Order`, `OrderItem`.
- Seed sample transaction data.
- Add database health check probe to `/api/v1/health`.
