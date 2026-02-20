# Alpha Quickstart

Goal: run your first PyIgnite API project in under 10 minutes.

## Prerequisites

- Python 3.12+
- `uv` installed and available in `PATH`
- local shell with write access to your workspace

## 1) Create a new API project

```bash
pyignite new myapi --profile api --template fastapi
cd myapi
```

Expected result:

- project files generated
- `src/` layout ready
- `pyignite.toml` present

## 2) Install dependencies

```bash
uv sync --extra dev
```

Expected result:

- virtual environment resolved
- runtime + dev tools installed

## 3) Start the API

```bash
uv run pyignite run
```

Expected result:

- server starts on `127.0.0.1:8000` (unless overridden)
- `GET /health` returns `{"status": "ok"}`

Use another terminal to verify quickly:

```bash
curl http://127.0.0.1:8000/health
```

## 4) Run the dev loop

```bash
uv run pyignite dev
```

Expected result:

- file changes in `src/` or `tests/` trigger reload and checks
- terminal shows cycle summaries and step outcomes

## 5) Validate quality gates

```bash
uv run pyignite test
uv run pyignite check
```

Expected result:

- baseline health test passes
- check pipeline finishes with deterministic status output

## Success checklist

- [ ] `pyignite new` generated project successfully
- [ ] dependencies installed with `uv sync --extra dev`
- [ ] `/health` returns `{"status": "ok"}`
- [ ] `pyignite dev` reacts to file changes
- [ ] `pyignite test` and `pyignite check` pass

## If something fails

Use `docs/troubleshooting-alpha.md` for common fixes, then report issues with `docs/alpha-feedback-template.md`.
