main:
    uv run __init__.py

lint:
    uv run pyright
    uv run ruff check

format:
    uv run ruff format
