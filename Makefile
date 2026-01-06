DB_PATH ?= noscroll.db

.PHONY: lint test ci dev reset-demo

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

ci: lint test

dev:
	DB_PATH=$(DB_PATH) uv run uvicorn app.main:app --reload --port 8000

# Requires server running via: make dev
demo:
	DB_PATH=$(DB_PATH) PYTHONPATH=. uv run python tools/demo.py

# Example: EMAIL=demo@example.com DAYS=365 make send-digests
send-digests:
	DB_PATH=$(DB_PATH) PYTHONPATH=. uv run python tools/send_digests.py

reset-demo:
	DB_PATH=$(DB_PATH) PYTHONPATH=. uv run python -c "import os; from storage.sqlite_store import SQLiteStore; s=SQLiteStore(db_path=os.environ.get('DB_PATH','noscroll.db')); s.reset_demo('demo@example.com','demo'); s.seed_demo('demo@example.com','demo'); print('ok')"
