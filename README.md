# PyIgnite

The developer toolchain for Python APIs.

## TL;DR

```bash
pyignite new myapi --profile api --template fastapi
cd myapi
uv sync --extra dev
uv run pyignite run
```

## Core Commands

```bash
pyignite new <name> --profile api --template fastapi
pyignite dev
pyignite run
pyignite test
pyignite lint
pyignite fmt
pyignite check
```

## Quick Navigation

- Docs index: [docs/README.md](docs/README.md)
- Alpha quickstart: [docs/getting-started/quickstart-alpha.md](docs/getting-started/quickstart-alpha.md)
- Troubleshooting: [docs/getting-started/troubleshooting-alpha.md](docs/getting-started/troubleshooting-alpha.md)
- Release checklist: [docs/release/release-alpha-checklist.md](docs/release/release-alpha-checklist.md)

## Docs by Section

- Getting Started: [docs/getting-started/README.md](docs/getting-started/README.md)
- Reference: [docs/reference/README.md](docs/reference/README.md)
- Dev Loop: [docs/dev-loop/README.md](docs/dev-loop/README.md)
- Quality and Performance: [docs/quality/README.md](docs/quality/README.md)
- Release and Feedback: [docs/release/README.md](docs/release/README.md)
- Architecture Decisions: [docs/adr/README.md](docs/adr/README.md)

## Product Scope (v1 alpha)

- FastAPI-first API scaffold
- No DB scaffolding by default
- Fast local loop with deterministic checks

## Roadmap

1. M1 - Foundations (CLI + Config)
2. M2 - FastAPI Scaffold (No DB)
3. M3 - Dev Loop (Vite-like)
4. M4 - Quality, Perf, DX Hardening
5. M5 - Internal Alpha Release

## License

MIT
