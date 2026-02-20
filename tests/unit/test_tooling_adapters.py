from pathlib import Path
import subprocess
from typing import Sequence

import pytest

from pyignite.config import (
    ChecksSection,
    DevSection,
    ProjectSection,
    PyIgniteConfig,
    RunSection,
    ToolingSection,
)
from pyignite.tooling import ToolAdapters, ToolKey, ToolNotAvailableError


class FakeRunner:
    def __init__(self, return_code: int, stdout: str = "", stderr: str = "") -> None:
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.last_command: tuple[str, ...] | None = None
        self.last_cwd: Path | None = None

    def run(self, command: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        self.last_command = tuple(command)
        self.last_cwd = cwd
        return subprocess.CompletedProcess(
            args=list(command),
            returncode=self.return_code,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def _config(tmp_path: Path) -> PyIgniteConfig:
    return PyIgniteConfig(
        root_dir=tmp_path,
        file_path=tmp_path / "pyignite.toml",
        project=ProjectSection(),
        tooling=ToolingSection(),
        dev=DevSection(),
        run=RunSection(),
        checks=ChecksSection(),
    )


def test_missing_tool_raises_actionable_error(tmp_path: Path) -> None:
    adapters = ToolAdapters(config=_config(tmp_path), which=lambda _: None)

    with pytest.raises(ToolNotAvailableError, match="Configured runner") as exc_info:
        adapters.ensure_available(ToolKey.LINTING)

    assert "[tooling].packaging" in exc_info.value.hint


def test_run_propagates_subprocess_exit_and_output(tmp_path: Path) -> None:
    runner = FakeRunner(return_code=7, stdout="out", stderr="err")
    adapters = ToolAdapters(
        config=_config(tmp_path),
        runner=runner,
        which=lambda _: "/usr/bin/tool",
    )

    result = adapters.run(ToolKey.TESTING, args=("-q",))

    assert result.command == ("uv", "run", "pytest", "-q")
    assert result.exit_code == 7
    assert result.stdout == "out"
    assert result.stderr == "err"
    assert runner.last_command == ("uv", "run", "pytest", "-q")
    assert runner.last_cwd == tmp_path


def test_tooling_config_controls_executable_name(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config = PyIgniteConfig(
        root_dir=config.root_dir,
        file_path=config.file_path,
        project=config.project,
        tooling=ToolingSection(packaging="my-uv", linting="my-ruff", testing="my-pytest"),
        dev=config.dev,
        run=config.run,
        checks=config.checks,
    )
    runner = FakeRunner(return_code=0)
    adapters = ToolAdapters(config=config, runner=runner, which=lambda _: "/usr/bin/tool")

    lint_result = adapters.run(ToolKey.LINTING, args=("check", "."))
    test_result = adapters.run(ToolKey.TESTING)
    package_result = adapters.run(ToolKey.PACKAGING, args=("--version",))

    assert lint_result.command == ("my-uv", "run", "my-ruff", "check", ".")
    assert test_result.command == ("my-uv", "run", "my-pytest")
    assert package_result.command[0] == "my-uv"
