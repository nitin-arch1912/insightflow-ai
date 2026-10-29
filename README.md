# InsightFlow AI

> AI-powered business intelligence for small and medium businesses.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Status

**Phase 1 — Project Foundation** (Week 1)

The API skeleton is running. Database, frontend, and AI layers come next.

---

## What Is InsightFlow AI?

InsightFlow AI is a business intelligence platform that lets users:

- Import sales and order data from CSV files.
- View revenue, orders, and customer metrics on a dashboard.
- Ask business questions in plain English.
- Get answers backed by real database results, not AI guesses.
- Identify unusual performance changes automatically.

---

## Quick Start (Development)

### Prerequisites

| Tool | Version |
|---|---|
| Python | ≥ 3.11 |
| Git | ≥ 2.40 |
| Node.js | ≥ 20 (frontend, later) |
| Docker Desktop | ≥ 24 (database, later) |

### 1. Clone the repository

```powershell
git clone https://github.com/<your-username>/insightflow-ai.git
cd insightflow-ai
```

### 2. Set up the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure environment

```powershell
Copy-Item .env.example .env
# Edit .env if needed — defaults work for local development
```

### 4. Start the API

```powershell
uvicorn app.main:app --reload --port 8000
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API documentation.

### 5. Run tests

```powershell
pytest tests/ -v
```

---

## Project Structure

```
insightflow-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/        ← Route handlers
│   │   ├── core/          ← Config and logging
│   │   └── main.py        ← FastAPI entry point
│   └── tests/             ← pytest test suite
├── docs/
│   ├── architecture.md
│   ├── PROJECT_STATUS.md  ← Current project state
│   └── decisions/         ← Architecture decision records
├── data/samples/          ← Sample CSV files (Phase 3+)
├── .env.example
└── README.md
```

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture overview.

Key decisions:

- **Modular monolith** — one codebase, clear module boundaries, easy to run and test locally. See [ADR-001](docs/decisions/001-monolith-first.md).
- **FastAPI** — automatic OpenAPI docs, type-safe request/response, async support.
- **Environment-based config** — no secrets in code.

---

## Development Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Project foundation | 🟡 In progress |
| 2 | Backend foundations | ⏳ Pending |
| 3 | Database and business data | ⏳ Pending |
| 4 | Business analytics | ⏳ Pending |
| 5 | Frontend dashboard | ⏳ Pending |
| 6 | CSV data ingestion | ⏳ Pending |
| 7 | Natural-language analytics | ⏳ Pending |
| 8–14 | AI, ML, security, deployment | ⏳ Pending |

---

## API Reference

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Quick health probe |
| `/api/v1/health` | GET | Versioned health check |
| `/docs` | GET | OpenAPI UI |

---

## Contributing

This project is a learning-focused build. Contributions, questions, and code reviews are welcome.

---

## License

MIT — see [LICENSE](LICENSE).
