# InsightFlow AI — Project Status

> **Living document.** Update this file at the end of every milestone.
> The goal: anyone (including future-you after a break) can read this file
> and know exactly where the project stands and what to do next.

---

## Current State

| Field | Value |
|---|---|
| **Phase** | 1 — Project Foundation |
| **Milestone** | 1 — Repository, environment, and health endpoint |
| **Date** | 2026-10-29 |
| **Status** | 🟡 In progress — awaiting test verification |

---

## Completed Features

- [x] Git repository initialized (`main` branch)
- [x] Python virtual environment (`backend/.venv`)
- [x] FastAPI application skeleton (`backend/app/main.py`)
- [x] Environment-based configuration (`backend/app/core/config.py`)
- [x] Structured logging (`backend/app/core/logging.py`)
- [x] Health endpoint at `/health` and `/api/v1/health`
- [x] Root redirect to `/docs`
- [x] 8 pytest tests covering health endpoint (happy path + failure cases)
- [x] `.gitignore`, `.env.example`, README scaffold
- [x] Architecture decision record: ADR-001 (modular monolith)

---

## Current Architecture

```
HTTP Request
    │
    ▼
FastAPI App (app/main.py)
    │
    ├─ /health              ← bare health check
    ├─ /docs                ← OpenAPI UI (auto-generated)
    └─ /api/v1/
        └─ /health          ← versioned health check (app/api/v1/health.py)
                                    │
                                    └─ app/core/config.py   (Settings)
                                    └─ app/core/logging.py  (Logger)
```

No database. No AI. No frontend. That comes next.

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

---

## Verified Tests

> ⚠️ Not yet verified — run the commands below and update this section.

```
pytest tests/ -v
```

Expected output (8 tests):
```
tests/test_health.py::TestRootHealth::test_returns_200          PASSED
tests/test_health.py::TestRootHealth::test_status_is_ok         PASSED
tests/test_health.py::TestRootHealth::test_version_is_present   PASSED
tests/test_health.py::TestApiV1Health::test_returns_200         PASSED
tests/test_health.py::TestApiV1Health::test_status_is_ok        PASSED
tests/test_health.py::TestApiV1Health::test_version_matches_config PASSED
tests/test_health.py::TestApiV1Health::test_environment_is_present PASSED
tests/test_health.py::TestApiV1Health::test_response_shape      PASSED
tests/test_health.py::TestRootRedirect::test_redirects_to_docs  PASSED
tests/test_health.py::TestNegativeCases::test_unknown_route_returns_404 PASSED
tests/test_health.py::TestNegativeCases::test_wrong_method_returns_405  PASSED
```

---

## Known Issues

- Docker Desktop not installed — needed for Phase 3 (PostgreSQL).
- No database — the backend stores and retrieves nothing yet.
- No authentication — the health endpoint is publicly accessible.
- CORS is wide-open in development mode — tighten before production.

---

## Pending Decisions

| Decision | Options | Status |
|---|---|---|
| Frontend charting library | Recharts vs Nivo vs Victory | Deferred to Phase 5 |
| AI provider | OpenAI API vs Ollama (local) | Deferred to Phase 7 |
| Cloud platform | Render vs Railway vs GCP | Deferred to Phase 12 |

---

## Important Commands

```powershell
# Activate virtual environment (run from backend/)
.venv\Scripts\Activate.ps1

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Check a running endpoint
Invoke-RestMethod -Uri http://localhost:8000/health

# Deactivate virtual environment
deactivate
```

---

## Next Milestone

**Phase 2 — Backend Foundations**
- Consistent error response format (RFC 7807 Problem Details)
- Request ID middleware for tracing
- 404 and 422 custom handlers
- OpenAPI documentation clean-up
- `GET /api/v1/info` endpoint with build metadata
