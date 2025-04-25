lint:
    uv run pyright
    uv run ruff check

format:
    uv run ruff format

strip-types: format lint
    uv run scripts/strip_types.py

install-addon:
    uv run scripts/install_addon.py

install-addon-full: strip-types install-addon

