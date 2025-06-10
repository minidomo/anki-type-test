lint:
    uv run check-jsonschema --schemafile schema.config.json plugin.config.json src/config.json
    uv run pyright
    uv run ruff check

format:
    uv run ruff format

build: format lint
    uv run scripts/strip_types.py
    uv run scripts/gen_manifest.py

install-addon *args:
    uv run scripts/install_addon.py {{args}}

package: build
    uv run scripts/zip_addon.py

clean:
    uv run scripts/clean.py out dist