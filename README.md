# PyIgnite

<p align="center">
  <strong>The developer toolchain for Python APIs</strong><br/>
  Fast scaffold, fast feedback loop, opinionated defaults.
</p>

<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/status-alpha_internal-lightgrey">
  <img alt="Python" src="https://img.shields.io/badge/python-3.12%2B-blue">
  <img alt="FastAPI" src="https://img.shields.io/badge/profile-fastapi-009688">
  <img alt="Uvicorn" src="https://img.shields.io/badge/server-uvicorn-2C3E50">
  <img alt="uv" src="https://img.shields.io/badge/package_manager-uv-6A5ACD">
  <img alt="Ruff" src="https://img.shields.io/badge/lint%2Fformat-ruff-D7FF64">
  <img alt="Pyright" src="https://img.shields.io/badge/types-pyright-2F74C0">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## Why PyIgnite?

Python API teams often lose time on repetitive setup and fragmented tooling:

- project bootstrap differs from repo to repo
- watch/reload behavior is inconsistent
- lint/test/type commands are scattered
- onboarding is slow and error-prone

**PyIgnite** brings a Vite-like experience to Python APIs:

- instant-ish local loop
- strong conventions
- minimal configuration
- one CLI surface for daily workflows

---

## Product Direction (v1)

### Target persona

**Backend API teams** (FastAPI-first).

### Product promise

A new API project should be runnable in minutes, and the save -> feedback loop should feel fast and predictable.

### Scope

- `pyignite new`
- `pyignite dev`
- `pyignite run`
- `pyignite test`
- `pyignite lint`
- `pyignite fmt`
- `pyignite check`

### Non-goals for v1 alpha

- broad plugin ecosystem
- Flask/Litestar parity
- DB scaffolding by default
- advanced CI generation

---

## Recommended Tech Stack

PyIgnite is built with a pragmatic Python-native stack:

- **Runtime**: Python `3.12+`
- **Packaging / env**: `uv`, `pyproject.toml`, `hatchling`
- **CLI UX**: `Typer` + `Rich`
- **Config**: `TOML` + `pydantic-settings`
- **Watch loop**: `watchfiles`
- **Process orchestration**: `anyio` + subprocess
- **Adapters (managed tools)**: `uvicorn`, `ruff`, `pytest`, `pyright`
- **Testing**: `pytest`, end-to-end command tests
- **Quality gates**: `ruff`, `pyright`, `pre-commit`
- **Release flow**: `commitizen` + GitHub Actions

### Why this stack?

- fast to ship
- easy to maintain
- aligned with Python ecosystem standards
- excellent developer experience without over-engineering

---

## FastAPI-first Philosophy (No DB by default)

For v1, scaffolding stays intentionally minimal:

- clean project structure
- health endpoint
- baseline tests
- no ORM/migrations by default

This keeps startup friction low and gives teams freedom to choose their data layer.

---

## Command Model

```bash
pyignite new myapi --profile api --template fastapi
pyignite dev
pyignite run
pyignite test
pyignite lint
pyignite fmt
pyignite check
```

### Command expectations

- **idempotent** by default
- **clear exit codes** for local + CI use
- **predictable output** with actionable errors
- **sensible defaults** over verbose setup

### v1 command specification

- Command contract: `docs/command-contract-v1.md`
- Deferred scope ADR: `docs/adr/0001-defer-v1-non-goals.md`
- Config example (API profile): `docs/examples/pyignite.toml`
- FastAPI scaffold layout: `docs/fastapi-scaffold-template.md`
- Dev incremental checks behavior: `docs/devloop-incremental-checks.md`
- Dev loop terminal UX: `docs/devloop-terminal-ux.md`
- E2E testing guide: `docs/e2e-testing.md`
- Performance benchmarks: `docs/perf-benchmarks.md`
- Alpha perf baseline: `docs/perf-baseline-alpha.md`
- Alpha quickstart: `docs/quickstart-alpha.md`
- Alpha troubleshooting: `docs/troubleshooting-alpha.md`
- Alpha feedback template: `docs/alpha-feedback-template.md`

---

## Roadmap (Internal Alpha)

The project is organized in milestones:

1. **M1 - Foundations (CLI + Config)**
2. **M2 - FastAPI Scaffold (No DB)**
3. **M3 - Dev Loop (Vite-like)**
4. **M4 - Quality, Perf, DX Hardening**
5. **M5 - Internal Alpha Release**

Detailed issues are tracked in GitHub with labels by:

- `type:*`
- `area:*`
- `priority:*`
- `stage:alpha`

---

## Performance and DX Targets

Internal alpha targets:

- **Time-to-first-run**: `new -> API up` in under 2 minutes
- **Save-to-feedback** in dev loop: under about 1.5s on a sample project
- **Zero-config success rate**: above 90% for happy path
- deterministic `check` pipeline output

---

## Contributing (Early Stage)

PyIgnite is in **internal alpha planning and execution** mode.

If you contribute:

- keep the core small
- preserve command determinism
- optimize for feedback speed
- avoid widening v1 scope without product justification

---

## License

MIT
