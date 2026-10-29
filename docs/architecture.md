# InsightFlow AI — Architecture

> This document is updated at each phase. See `docs/PROJECT_STATUS.md` for
> current milestone status, and `docs/decisions/` for architecture decision records.

---

## Phase 1 Architecture (Current)

A single FastAPI process with no external dependencies. No database. No AI.

```
┌─────────────────────────────────────────────────┐
│                  HTTP Clients                   │
│         (curl, browser, Postman, tests)         │
└────────────────────┬────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────┐
│             FastAPI Application                 │
│                                                 │
│  ┌──────────┐   ┌──────────────┐               │
│  │  /health │   │ /api/v1/     │               │
│  │ (root)   │   │   health     │               │
│  └──────────┘   └──────┬───────┘               │
│                        │                        │
│                 ┌──────▼───────┐               │
│                 │  core/       │               │
│                 │  config.py   │               │
│                 │  logging.py  │               │
│                 └──────────────┘               │
└─────────────────────────────────────────────────┘
```

### Key Design Choices

| Choice | Reason |
|---|---|
| FastAPI | Automatic OpenAPI docs, async support, Pydantic integration |
| Pydantic response models | Response shape is validated, documented, and typed |
| `pydantic-settings` | Environment variables are typed and fail loudly if misconfigured |
| Named loggers per module | Log output shows the source; easy to filter |
| `create_app()` factory | Tests get a fresh app without shared global state |

---

## Planned Architecture (Phase 3+)

```
Browser
  │
  ▼
React Frontend (Vite + TypeScript)
  │ HTTP/JSON
  ▼
FastAPI Backend
  ├── api/v1/          ← Route handlers (thin layer)
  ├── services/
  │   ├── analytics/   ← Business metrics (deterministic SQL)
  │   ├── ai/          ← LLM orchestration and tool calling
  │   └── ml/          ← Anomaly detection (Phase 10)
  ├── repositories/    ← All database access (one place)
  ├── models/          ← SQLAlchemy ORM models
  └── schemas/         ← Pydantic request/response schemas
  │
  ▼
PostgreSQL Database
```

Additions are introduced one phase at a time with a new ADR when needed.
