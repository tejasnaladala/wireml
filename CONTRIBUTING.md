# Contributing to WireML

Welcome. WireML is an open-source node-graph ML workbench — contributions of nodes, templates, runtime implementations, and docs are all valuable.

## Development setup

```bash
git clone https://github.com/nautilus4707/wireml
cd wireml
pnpm install
cd apps/runtime && uv sync && cd -
pnpm dev         # one terminal: UI
pnpm dev:runtime # another terminal: Python runtime (optional)
```

## Adding a new node

1. Add the `NodeSchema` entry to [`packages/nodes/src/registry.ts`](packages/nodes/src/registry.ts).
2. Implement the web-side runner in [`apps/web/src/runtime/WebGraphRunner.ts`](apps/web/src/runtime/WebGraphRunner.ts). If the node requires a large model or native kernel, mark it `localOnly: true` in its capability.
3. (Optional / if `localOnly`) Implement the matching server runner under [`apps/runtime/wireml_runtime/nodes/`](apps/runtime/wireml_runtime/nodes/).
4. Add a test in `apps/web/src/**/*.test.ts` and `apps/runtime/tests/`.
5. If the node enables a new canonical pipeline, add a template JSON to `packages/templates/src/`.

## Code style

- **TypeScript:** strict mode, prefer functional composition, avoid implicit `any`.
- **Python:** `ruff` for formatting/linting, `mypy` for types, no bare `except`.
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

## Running the test suite

```bash
pnpm test                 # frontend (vitest)
pnpm -w typecheck         # type-check all packages
cd apps/runtime && uv run pytest
```
