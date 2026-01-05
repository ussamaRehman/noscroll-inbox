.PHONY: lint test ci dev

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

ci: lint test

dev:
	uv run uvicorn app.main:app --reload --port 8000

# Requires server running via: make dev
demo:
	uv run python tools/demo.py

# Example: EMAIL=demo@example.com DAYS=365 make send-digests
send-digests:
	uv run python tools/send_digests.py
