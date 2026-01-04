.PHONY: lint test ci dev

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -q

ci: lint test

dev:
	uv run uvicorn app.main:app --reload --port 8000
