# CI Notes (Scaffold)

Planned baseline pipeline stages:

- install (uv sync)
- lint (ruff check .)
- format check (ruff format --check .)
- type-check (pyright)
- test (pytest)
- e2e (`scripts/run_e2e.sh`)
- perf guardrails (`scripts/run_benchmarks.sh`, fail mode)
- package build validation (`.github/workflows/python-package.yml`)
- trusted publishing (`.github/workflows/publish.yml`, TestPyPI -> PyPI)
- GitHub release automation (`.github/workflows/publish.yml`, notes + artifacts)

This file documents the intended shape before a full workflow is added.
