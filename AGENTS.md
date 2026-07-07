# AGENTS.md

## Project
FastAPI backend for document OCR/extraction, semantic comparison (deviation detection), and RAG. Single client project — keep things simple, avoid overengineering.

## Stack
- FastAPI + Pydantic v2
- PostgreSQL + asyncpg (raw SQL — **no ORM**, no SQLAlchemy)
- Migrations: dbmate (timestamp-prefixed .sql files in `migrations/`)
- `make dev` for shorter run command
- Package manager: uv (`uv add`, `uv run`, `pyproject.toml` + `uv.lock`)
- Testing: pytest + httpx against a real test Postgres (no mocks — no ORM to mock against)

## Best practices
- Type hints on every function signature; prefer Pydantic models over raw dicts for any structured data crossing a boundary.
- Async all the way through — no blocking calls inside async route handlers.
- Use `Annotated[..., Depends(...)]` for dependency injection.
- Return typed response models from routes; let Pydantic handle serialization.
- Never hold a DB connection open across a long-running LLM/OCR call.
- Never overwrite extraction/processing results — version them.
- No repository for a module unless it actually owns a DB table.
- Config and secrets only via `.env` + `pydantic-settings`.
- Long-running/GPU work runs in a separate worker process, never inside a request handler.
- Don't add abstractions speculatively — add them when a concrete problem forces it.
- One logical concern per file: routes, schemas, repository (SQL), and service (business logic) each live in their own file — never mixed in one.
- Keep files small: if a file crosses ~200–300 lines, split it.
- A function should do one thing; if a service method needs a comment to separate "steps," extract a helper function instead.
- No god files — a file named `utils.py`/`helpers.py` that accumulates unrelated logic is a smell; name files after what they actually do.
- Module boundaries stay physical (separate files/folders), never merged for convenience even if small.
- Reusable, module-agnostic code (base Pydantic mixins, pagination helpers, generic error types) goes in a shared `common/` folder — not duplicated per module, and not dumped into whichever module needed it first.