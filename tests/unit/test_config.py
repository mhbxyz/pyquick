from pathlib import Path

import pytest

from pyignite.config import ConfigError, load_config


def _write_config(tmp_path: Path, body: str) -> None:
    (tmp_path / "pyignite.toml").write_text(body, encoding="utf-8")


def test_load_config_returns_defaults_when_file_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path)

    assert config.project.profile == "api"
    assert config.project.template == "fastapi"
    assert config.tooling.packaging == "uv"
    assert config.tooling.linting == "ruff"
    assert config.tooling.testing == "pytest"
    assert config.tooling.typing == "pyright"
    assert config.tooling.running == "uvicorn"
    assert config.dev.watch == ("src", "tests")
    assert config.checks.pipeline == ("lint", "type", "test")


def test_load_config_with_valid_partial_sections(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[run]
port = 9000

[checks]
pipeline = ["type", "test", "lint"]
""".strip(),
    )

    config = load_config(tmp_path)

    assert config.run.port == 9000
    assert config.run.host == "127.0.0.1"
    assert config.checks.pipeline == ("type", "test", "lint")


def test_load_config_rejects_unknown_top_level_key(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[foo]
bar = "baz"
""".strip(),
    )

    with pytest.raises(ConfigError, match="Unknown key"):
        load_config(tmp_path)


def test_load_config_rejects_unknown_section_key(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[run]
port = 8000
extra = true
""".strip(),
    )

    with pytest.raises(ConfigError, match="Unknown key"):
        load_config(tmp_path)


def test_load_config_rejects_old_tooling_keys(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[tooling]
uv = "uv"
""".strip(),
    )

    with pytest.raises(ConfigError, match="Unknown key"):
        load_config(tmp_path)


def test_load_config_rejects_invalid_profile(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[project]
profile = "flask"
""".strip(),
    )

    with pytest.raises(ConfigError, match="must be `api`"):
        load_config(tmp_path)


def test_load_config_rejects_invalid_type(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[dev]
reload = "yes"
""".strip(),
    )

    with pytest.raises(ConfigError, match="must be a boolean"):
        load_config(tmp_path)


def test_load_config_rejects_unknown_pipeline_step(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        """
[checks]
pipeline = ["lint", "security", "test"]
""".strip(),
    )

    with pytest.raises(ConfigError, match="unsupported step"):
        load_config(tmp_path)


def test_load_config_rejects_invalid_toml(tmp_path: Path) -> None:
    _write_config(tmp_path, "[run\nport = 8000")

    with pytest.raises(ConfigError, match="Invalid TOML"):
        load_config(tmp_path)
