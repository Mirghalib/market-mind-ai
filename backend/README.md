# Market Mind AI — Backend

AI SaaS backend built with **FastAPI** and **SQLAlchemy (async)** using a clean, layered architecture.

## Tech Stack

| Layer        | Choice                                  |
| ------------ | --------------------------------------- |
| Web framework| FastAPI                                 |
| Validation   | Pydantic v2 + pydantic-settings         |
| Database     | PostgreSQL + SQLAlchemy 2.0 (async)     |
| Migrations   | Alembic                                 |
| Auth (stub)  | JWT (python-jose), bcrypt (passlib)     |
| Testing      | pytest + pytest-asyncio + httpx         |

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
│   ├── services/       # Business logic (BaseService starter)
│   ├── prompts/        # LLM prompt templates
│   ├── utils/          # Reusable helpers
│   └── dependencies/   # Reusable FastAPI dependencies
├── tests/              # pytest suite
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
cp .env.example .env             # then edit values

# 4. Run the server
uvicorn main:app --reload
```

Interactive docs are available at `http://localhost:8000/docs`.

## Testing

```bash
pytest -v
```

## Scripts

| Purpose      | Command                                  |
| ------------ | ---------------------------------------- |
| Run dev server | `uvicorn main:app --reload --port 8000` |
| Run tests    | `pytest -v`                              |
| Generate migration | `alembic revision --autogenerate -m "message"` |
| Apply migration | `alembic upgrade head`               |
