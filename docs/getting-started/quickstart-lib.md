# Library Quickstart

[Project README](../../README.md) · [Docs Index](../README.md) · [Getting Started](README.md)

Goal: create and validate your first PyQuick Python library project.

Need CLI installation first? Use the [Install guide](install.md).

## Prerequisites

- Python 3.12+
- `uv` installed and available in `PATH`

## 1) Create a new library project

```bash
pyqck new mylib --profile lib
cd mylib
```

Expected result:

- `src/` package scaffold generated
- baseline test file generated
- `pyquick.toml` contains `profile = "lib"`

## 2) Install dependencies

```bash
pyqck install
```

Expected result:

- virtual environment created
- dev tooling installed (`pytest`, `ruff`, `pyright`)

## 3) Run baseline quality flow

```bash
pyqck test
pyqck check
```

Expected result:

- baseline library test passes
- `check` pipeline completes with deterministic status output

## Success checklist

- [ ] `pyqck new --profile lib` generated project successfully
- [ ] dependencies installed with `pyqck install`
- [ ] `pyqck test` passes
- [ ] `pyqck check` passes

## See Also

- [Getting Started index](README.md)
- [Install guide](install.md)
- [Alpha troubleshooting](troubleshooting-alpha.md)
