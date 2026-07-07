dev:
	uv run fastapi dev app/main.py --port $${PORT:-8001}

lint:
	uv run ruff check .

typecheck:
	uv run pyrefly check

check: lint typecheck