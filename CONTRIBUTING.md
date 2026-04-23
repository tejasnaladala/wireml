# Contributing to WireML

## Dev setup

```bash
git clone https://github.com/tejasnaladala/wireml
cd wireml
uv sync --extra dev
uv run pytest
uv run wireml           # launch the TUI against your checkout
```

## Adding a node

1. Add a `NodeSchema` to `wireml/registry.py`.
2. Implement the runner in `wireml/nodes/<category>.py` decorated with `@engine.register("<schema.id>")`.
3. If the runner needs torch / transformers / mlx, import them inside the function body (lazy) and mark the schema's `Capability` appropriately.
4. Add a pytest at `tests/test_<category>.py`.
5. If the node enables a new canonical pipeline, add a `Template` to `wireml/templates.py`.

## Style

- `ruff check wireml tests` must pass.
- Type-annotate function signatures.
- No `print()` — use `logging.getLogger(__name__)`.
- Commits follow conventional-commit prefixes: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
