main:
    uv run __init__.py

lint:
    uv run pyright
    uv run ruff check

format:
    uv run ruff format

install-addon:
    uv run scripts/anki_addon_import.py
