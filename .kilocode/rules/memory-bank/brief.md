# ANVIL — Python Toolchain Orchestrator

---

## 0) Executive Summary

**Anvil** is a CLI that scaffolds, configures, and orchestrates Python projects — zero manual Makefiles, zero repetitive setup. It standardizes commands across repos and remains extensible via a clear plugin & profile system.

**Core commands** now include: `new · add · apply · check · test · cov · build · release · dev · run · fmt · lint`.

---

## 1) Command Surface (Spec)

All commands are **idempotent** and **project‑aware** (read `anvil.toml`). Where relevant, they fallback gracefully if a preferred tool is missing.

### `anvil new`
**Goal:** scaffold a new project according to a chosen profile (see §3).

Usage:
```bash
anvil new mylib --profile lib
anvil new myapi --profile api --template fastapi
```
Creates directory, structure, default `pyproject.toml`, and `anvil.toml`.

### `anvil dev`
**Goal:** run project in **watch mode** for tight feedback loops.
- Watches source/tests; runs `ruff check` + `pytest` or framework runner with reload.

### `anvil run`
**Goal:** run the **canonical executable** for the project.

Resolves entry via:
1. `project.scripts` in `pyproject.toml`.
2. `run.module` in `anvil.toml`.
3. `run.entry` (for ASGI/WSGI) with detected runner.
4. Fallback: `python -m <package>`.

### `anvil fmt`
Runs `ruff` (import sort) + `black` for formatting.

### `anvil lint`
Runs `ruff check` (no fix), optional `bandit`/`pip-audit`, optional type preflight.

### Existing commands
- **`check`** = `lint` + `fmt --check` + type-check
- **`test`** = run pytest
- **`cov`** = coverage run/report/html
- **`build`** = `uv build`
- **`release`** = Commitizen bump + tag (& PyPI in CI)
- **`apply`** = reconcile files to `anvil.toml`
- **`add`** = enable features (lint, test, etc.)

---

## 2) Configuration Model (`anvil.toml`)

```toml
[project]
name = "mylib"
package = "acme_core"
python = "3.11"
profile = "lib" # lib | cli | api | service | monorepo

[tooling]
runner = "uv"
tasker = "just"

[features]
lint = true
format = true
test = true
types = "pyright"
pre_commit = true
ci = "github"
release = true

[format]
engine = "black_and_ruff"
line_length = 80
paths = ["src", "tests"]

[lint]
security = false
paths = ["src", "tests"]

[dev]
watch = ["src", "tests"]
debounce_ms = 150

[run]
module = "acme_core.__main__"   # fallback if no console_script
entry = "acme_api:app"

[api]
template = "fastapi" # or flask, litestar, etc.

[types]
mode = "standard"

[ci]
python = ["3.11", "3.12"]
platforms = ["ubuntu-latest"]
```

---

## 3) Profiles

Profiles are **opinionated blueprints** that define structure and defaults.

### Built‑in Profiles

1) **`lib`** — Python library
```
src/<package>/__init__.py
tests/test_sanity.py
```
Defaults: `lint`, `format`, `test`, `types`, `pre_commit`, `release`

2) **`cli`** — CLI app
```
src/<package>/__main__.py  # Typer stub
pyproject.toml [project.scripts]
```
Defaults: adds console entry; `anvil run` executes script.

3) **`api`** — Web API (framework via `--template`)
```
anvil new myapi --profile api --template fastapi
anvil new myapi --profile api --template flask
```
- `fastapi` ⇒ dep `fastapi`, runner `uvicorn`.
- `flask` ⇒ dep `flask`, runner `flask --app`.
- Extensible by plugins: `--template django`, `litestar`, etc.

4) **`service`** — background service/worker
```
src/<package>/service.py
```
Defaults: runs as worker process with restart on change.

5) **`monorepo`** — workspace root
```
uv.toml [workspace]
packages/
```
Defaults: manages multiple child packages.

---

## 4) Plugin System

Plugins extend Anvil via entry points:
- `anvil.features` → adds new tooling modules
- `anvil.profiles` → new project profiles
- `anvil.hooks` → pre/post command hooks

They declare compatibility via `Requires-Anvil` metadata.

**Interfaces**
```python
class Feature(Protocol):
    def apply(self, ctx) -> None: ...

class Profile(Protocol):
    def scaffold(self, ctx) -> list[Patch]: ...
```

`Patch` = file merge / dep add / script append.

**UX:**
```bash
pipx install anvil-fastapi
anvil plugins list
anvil add fastapi
anvil new myapi --profile api --template fastapi
```

---

## 5) Developer Experience

- `anvil.toml` is single source of truth.
- Non‑zero exit codes on failure gates.
- `anvil --help` lists detected profiles and plugins.
- Telemetry off by default.

---

## 6) Implementation Plan

### Phase 1 — MVP (Weeks 2–4)
- Commands: `new`, `add`, `lint`, `fmt`, `check`, `test`, `build`, `run`, `dev`, `release`.
- Profiles: `lib`, `cli`, `api` (with `--template fastapi|flask`), `service`, `monorepo`.
- Basic templates and config writing.

### Phase 2 — Patch Engine (Weeks 5–7)
- TOML/YAML merge with comments.
- `anvil apply --plan` (dry‑run) and backups.

### Phase 3 — Plugins (Weeks 8–10)
- Entry point loader + example plugin `anvil-fastapi`.

### Phase 4 — Dev/Run polish (Weeks 11–12)
- Watch mode, framework reload.
- `pytest-testmon` optional integration.

### Phase 5 — CI/CD & Release (Weeks 13–15)
- GH Actions templates.
- PyPI publish workflow.

### Phase 6 — Documentation (Weeks 16–18)
- `mkdocs-material` site, tutorials, screencasts.

---

## 7) Example `anvil.toml`

### `lib`
```toml
[project]
name = "acme-core"
package = "acme_core"
python = "3.11"
profile = "lib"

[features]
lint = true
format = true
test = true
types = "pyright"
```

### `api`
```toml
[project]
name = "acme-api"
package = "acme_api"
python = "3.11"
profile = "api"

[api]
template = "fastapi"

[run]
entry = "acme_api:app"
```

---

## 8) Acceptance Criteria for v1.0
- `pipx install anvilkit` installs CLI.
- `anvil new` + `anvil dev` work flawlessly on macOS/Linux/Windows.
- `anvil fmt` and `anvil lint` are deterministic and fast (<1s on small repo).
- `anvil run` resolves proper entry for all profiles.
- `anvil apply --plan` shows clear patch list and preserves comments.
- Plugin loader detects and lists at least one plugin.
