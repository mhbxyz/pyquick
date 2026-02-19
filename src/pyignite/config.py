from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any

DEFAULT_CONFIG_FILE = "pyignite.toml"


@dataclass(slots=True, frozen=True)
class ProjectSection:
    name: str = "myapi"
    profile: str = "api"
    template: str = "fastapi"


@dataclass(slots=True, frozen=True)
class ToolingSection:
    packaging: str = "uv"
    linting: str = "ruff"
    testing: str = "pytest"
    typing: str = "pyright"
    running: str = "uvicorn"


@dataclass(slots=True, frozen=True)
class DevSection:
    reload: bool = True
    watch: tuple[str, ...] = ("src", "tests")
    debounce_ms: int = 200


@dataclass(slots=True, frozen=True)
class RunSection:
    app: str = "app.main:app"
    host: str = "127.0.0.1"
    port: int = 8000


@dataclass(slots=True, frozen=True)
class ChecksSection:
    pipeline: tuple[str, ...] = ("lint", "type", "test")
    stop_on_first_failure: bool = True


@dataclass(slots=True, frozen=True)
class PyIgniteConfig:
    root_dir: Path
    file_path: Path
    project: ProjectSection
    tooling: ToolingSection
    dev: DevSection
    run: RunSection
    checks: ChecksSection


class ConfigError(Exception):
    """Raised when pyignite.toml is invalid."""

    def __init__(self, message: str, hint: str) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


@dataclass(slots=True)
class ProjectConfig:
    """Backward-compatible alias kept during transition."""

    root_dir: Path


def load_config(root_dir: Path, file_name: str = DEFAULT_CONFIG_FILE) -> PyIgniteConfig:
    file_path = root_dir / file_name
    if not file_path.exists():
        return _default_config(root_dir=root_dir, file_path=file_path)

    try:
        raw = tomllib.loads(file_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(
            f"Invalid TOML in `{file_name}`: {exc}.",
            "Fix TOML syntax errors and retry.",
        ) from exc
    except OSError as exc:
        raise ConfigError(
            f"Could not read `{file_name}`.",
            "Check file permissions and retry.",
        ) from exc

    if not isinstance(raw, dict):
        raise ConfigError(
            f"`{file_name}` must contain TOML tables.",
            "Define top-level sections like `[project]` and `[tooling]`.",
        )

    return _parse_config(root_dir=root_dir, file_path=file_path, raw=raw)


def _default_config(root_dir: Path, file_path: Path) -> PyIgniteConfig:
    return PyIgniteConfig(
        root_dir=root_dir,
        file_path=file_path,
        project=ProjectSection(),
        tooling=ToolingSection(),
        dev=DevSection(),
        run=RunSection(),
        checks=ChecksSection(),
    )


def _parse_config(root_dir: Path, file_path: Path, raw: dict[str, Any]) -> PyIgniteConfig:
    _assert_allowed_keys(
        actual=raw,
        allowed={"project", "tooling", "dev", "run", "checks"},
        context="top-level",
    )

    project_raw = _read_table(raw, "project")
    tooling_raw = _read_table(raw, "tooling")
    dev_raw = _read_table(raw, "dev")
    run_raw = _read_table(raw, "run")
    checks_raw = _read_table(raw, "checks")

    project = _parse_project(project_raw)
    tooling = _parse_tooling(tooling_raw)
    dev = _parse_dev(dev_raw)
    run = _parse_run(run_raw)
    checks = _parse_checks(checks_raw)

    return PyIgniteConfig(
        root_dir=root_dir,
        file_path=file_path,
        project=project,
        tooling=tooling,
        dev=dev,
        run=run,
        checks=checks,
    )


def _read_table(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError(
            f"Section `[{key}]` must be a table.",
            f"Replace `[{key}]` with valid key/value pairs.",
        )
    return value


def _parse_project(raw: dict[str, Any]) -> ProjectSection:
    _assert_allowed_keys(raw, {"name", "profile", "template"}, context="[project]")

    name = _read_string(raw, "name", default="myapi", context="[project]")
    profile = _read_string(raw, "profile", default="api", context="[project]")
    template = _read_string(raw, "template", default="fastapi", context="[project]")

    if profile != "api":
        raise ConfigError(
            "`[project].profile` must be `api` in v1.",
            'Use `profile = "api"`.',
        )
    if template != "fastapi":
        raise ConfigError(
            "`[project].template` must be `fastapi` in v1.",
            'Use `template = "fastapi"`.',
        )

    return ProjectSection(name=name, profile=profile, template=template)


def _parse_tooling(raw: dict[str, Any]) -> ToolingSection:
    _assert_allowed_keys(
        raw,
        {"packaging", "linting", "testing", "typing", "running"},
        context="[tooling]",
    )

    return ToolingSection(
        packaging=_read_string(raw, "packaging", default="uv", context="[tooling]"),
        linting=_read_string(raw, "linting", default="ruff", context="[tooling]"),
        testing=_read_string(raw, "testing", default="pytest", context="[tooling]"),
        typing=_read_string(raw, "typing", default="pyright", context="[tooling]"),
        running=_read_string(raw, "running", default="uvicorn", context="[tooling]"),
    )


def _parse_dev(raw: dict[str, Any]) -> DevSection:
    _assert_allowed_keys(raw, {"reload", "watch", "debounce_ms"}, context="[dev]")

    reload_enabled = _read_bool(raw, "reload", default=True, context="[dev]")
    debounce_ms = _read_int(raw, "debounce_ms", default=200, context="[dev]")
    if debounce_ms < 0:
        raise ConfigError(
            "`[dev].debounce_ms` must be >= 0.",
            "Set `debounce_ms` to a non-negative integer.",
        )

    watch = _read_string_list(raw, "watch", default=["src", "tests"], context="[dev]")
    if not watch:
        raise ConfigError(
            "`[dev].watch` must contain at least one path.",
            'Set `watch = ["src"]` or another non-empty list.',
        )

    return DevSection(reload=reload_enabled, watch=tuple(watch), debounce_ms=debounce_ms)


def _parse_run(raw: dict[str, Any]) -> RunSection:
    _assert_allowed_keys(raw, {"app", "host", "port"}, context="[run]")

    app = _read_string(raw, "app", default="app.main:app", context="[run]")
    host = _read_string(raw, "host", default="127.0.0.1", context="[run]")
    port = _read_int(raw, "port", default=8000, context="[run]")

    if port < 1 or port > 65535:
        raise ConfigError(
            "`[run].port` must be between 1 and 65535.",
            "Set `port` to a valid TCP port.",
        )

    return RunSection(app=app, host=host, port=port)


def _parse_checks(raw: dict[str, Any]) -> ChecksSection:
    _assert_allowed_keys(raw, {"pipeline", "stop_on_first_failure"}, context="[checks]")

    pipeline = _read_string_list(
        raw, "pipeline", default=["lint", "type", "test"], context="[checks]"
    )
    allowed_steps = {"lint", "type", "test"}
    unknown_steps = [step for step in pipeline if step not in allowed_steps]
    if unknown_steps:
        unknown = ", ".join(sorted(set(unknown_steps)))
        raise ConfigError(
            f"`[checks].pipeline` includes unsupported step(s): {unknown}.",
            "Use only `lint`, `type`, and `test` in v1.",
        )
    if len(set(pipeline)) != len(pipeline):
        raise ConfigError(
            "`[checks].pipeline` must not contain duplicates.",
            "Remove repeated steps and retry.",
        )

    stop_on_first_failure = _read_bool(
        raw,
        "stop_on_first_failure",
        default=True,
        context="[checks]",
    )

    return ChecksSection(pipeline=tuple(pipeline), stop_on_first_failure=stop_on_first_failure)


def _assert_allowed_keys(actual: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(actual) - allowed)
    if not unknown:
        return

    if len(unknown) == 1:
        unknown_repr = f"`{unknown[0]}`"
    else:
        unknown_repr = ", ".join(f"`{item}`" for item in unknown)

    raise ConfigError(
        f"Unknown key(s) in {context}: {unknown_repr}.",
        "Remove unsupported keys or move them to a supported section.",
    )


def _read_string(raw: dict[str, Any], key: str, default: str, context: str) -> str:
    value = raw.get(key, default)
    if not isinstance(value, str):
        raise ConfigError(
            f"`{context}.{key}` must be a string.",
            f"Set `{key}` to a quoted string value.",
        )
    return value


def _read_bool(raw: dict[str, Any], key: str, default: bool, context: str) -> bool:
    value = raw.get(key, default)
    if not isinstance(value, bool):
        raise ConfigError(
            f"`{context}.{key}` must be a boolean.",
            f"Set `{key}` to `true` or `false`.",
        )
    return value


def _read_int(raw: dict[str, Any], key: str, default: int, context: str) -> int:
    value = raw.get(key, default)
    if not isinstance(value, int):
        raise ConfigError(
            f"`{context}.{key}` must be an integer.",
            f"Set `{key}` to an integer value.",
        )
    return value


def _read_string_list(raw: dict[str, Any], key: str, default: list[str], context: str) -> list[str]:
    value = raw.get(key, default)
    if not isinstance(value, list):
        raise ConfigError(
            f"`{context}.{key}` must be an array of strings.",
            f'Set `{key}` to a TOML array like `["a", "b"]`.',
        )
    if not all(isinstance(item, str) for item in value):
        raise ConfigError(
            f"`{context}.{key}` must only contain strings.",
            f"Use string entries in `{key}`.",
        )
    return value
