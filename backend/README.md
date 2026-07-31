# Market Mind AI — Backend

AI SaaS backend built with **FastAPI** and **SQLAlchemy (async)** using a clean, layered architecture.

## Tech Stack

| Layer         | Choice                                  |
| ------------- | --------------------------------------- |
| Web framework | FastAPI                                 |
| Validation    | Pydantic v2 + pydantic-settings         |
| Database      | PostgreSQL + SQLAlchemy 2.0 (async)     |
| Migrations    | Alembic                                 |
| Auth          | JWT (python-jose, HS256) + bcrypt       |
| RBAC          | Roles + permissions (admin / user)      |
| AI pipeline   | Groq (Llama) / OpenAI / Anthropic       |
| Testing       | pytest + pytest-asyncio + httpx         |

## Project Structure

```
backend/
├── app/
│   ├── api/            # HTTP layer: versioned routers + thin endpoints
│   ├── core/           # Config, security, logging
│   ├── database/       # Engine, session factory, Base
│   ├── middleware/     # Custom ASGI/Starlette middleware
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic request/response schemas
│   ├── services/       # Business logic (incl. services/ai AI pipeline)
│   ├── seeders/        # Idempotent role/permission/admin seeding
│   ├── prompts/        # LLM prompt templates
│   └── dependencies/   # Reusable FastAPI dependencies (auth, RBAC)
├── tests/              # pytest suite (83 tests)
├── main.py             # App entrypoint (uvicorn main:app)
├── requirements.txt
└── .env.example
```

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env             # then edit values (DB URL, GROQ_API_KEY, SECRET_KEY)

# 4. Run migrations + seed the RBAC baseline
alembic upgrade head
python -m app.seeders.seed_all   # roles, permissions, admin@marketmind.ai / Admin@123

# 5. Run the server
uvicorn main:app --reload --port 8000
```

Interactive docs are available at `http://localhost:8000/docs` (API under `/api/v1`).

## Scripts

| Purpose             | Command                                        |
| ------------------- | ---------------------------------------------- |
| Run dev server      | `uvicorn main:app --reload --port 8000`        |
| Run tests           | `pytest -v`                                    |
| Generate migration  | `alembic revision --autogenerate -m "message"` |
| Apply migration     | `alembic upgrade head`                         |
| Seed RBAC baseline  | `python -m app.seeders.seed_all`               |

## AI Provider

`AI_PROVIDER` selects the LLM vendor (`groq` default, `openai`, or `anthropic`); the matching
API key is read from `.env`. When the provider is rate-limited or unavailable,
`AI_FALLBACK_TO_MOCK=true` (default) degrades to a deterministic mock strategy so demos and
CI never hard-fail. Set it to `false` in production to surface real errors.
