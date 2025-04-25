lint:
    uv run pyright
    uv run ruff check

format:
    uv run ruff format

build: format lint
    uv run scripts/strip_types.py

install-addon-copy:
    uv run scripts/install_addon.py

install-addon: build install-addon-copy

package: build
    uv run scripts/zip_addon.py

clean:
    uv run scripts/clean.py out dist