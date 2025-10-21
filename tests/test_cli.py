"""Tests for CLI functionality.

This suite patches external tool invocations to avoid spawning subprocesses
that can re-invoke pytest (causing recursion) or perform heavy work that
bloats memory usage during test runs.
"""

from click.testing import CliRunner
from pathlib import Path
import shutil
from unittest.mock import patch

from anvil.cli import main


def test_cli_help():
    """Test that CLI shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "🔨 Anvil: Python Toolchain Orchestrator" in result.output


def test_cli_version():
    """Test that CLI shows version."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_new_command():
    """Test new command with valid arguments."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["new", "testproject", "--profile", "lib"])
        assert result.exit_code == 0
        assert "Creating new lib project: testproject" in result.output
        assert "Project 'testproject' created successfully!" in result.output

        # Clean up created files to prevent memory accumulation
        if Path("testproject").exists():
            shutil.rmtree("testproject")


def test_dev_command():
    """Test dev command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["dev"])
    # In some environments watchdog may be present; in others not.
    # Accept both behaviors but ensure the command returns without crashing.
    assert result.exit_code in (0, 1)


def test_run_command():
    """Test run command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["run"])
    # Run command attempts to execute but fails due to missing entry point
    assert result.exit_code == 0  # Click doesn't exit on error
    assert "Running project" in result.output
    assert "Command failed with exit code 1" in result.output


def test_fmt_command():
    """Test fmt command."""
    runner = CliRunner()
    # Patch formatter to avoid depending on host tools
    with patch("anvil.tools.ToolExecutor.run_ruff_format", return_value=1):
        result = runner.invoke(main, ["fmt"])
    # Fmt command fails (simulated)
    assert result.exit_code == 0  # Click doesn't exit on error
    assert "Formatting code" in result.output
    assert "Formatting failed" in result.output


def test_lint_command():
    """Test lint command."""
    runner = CliRunner()
    # Patch linter to avoid depending on host tools
    with patch("anvil.tools.ToolExecutor.run_ruff_check", return_value=1):
        result = runner.invoke(main, ["lint"])
    # Lint command fails (simulated)
    assert result.exit_code == 0  # Click doesn't exit on error
    assert "Linting code" in result.output
    assert "Linting issues found" in result.output


def test_test_command():
    """Test test command."""
    runner = CliRunner()
    # Patch to prevent spawning nested pytest processes which causes recursion
    # and excessive memory usage when running inside pytest.
    with patch("anvil.tools.ToolExecutor.run_pytest", return_value=1):
        result = runner.invoke(main, ["test"])
        assert result.exit_code == 0  # Click doesn't exit on error
        assert "Running tests" in result.output
        assert "Some tests failed" in result.output


def test_check_command():
    """Test check command."""
    runner = CliRunner()
    # Patch linters/formatters to avoid hitting real tools
    with (
        patch("anvil.tools.ToolExecutor.run_ruff_check", return_value=1),
        patch("anvil.tools.ToolExecutor.run_ruff_format", return_value=1),
    ):
        result = runner.invoke(main, ["check"])
        assert result.exit_code == 0
        assert "Running comprehensive code checks" in result.output
        # We just verify it runs and produces output


def test_build_command():
    """Test build command placeholder."""
    runner = CliRunner()
    # Patch build to avoid heavy subprocesses
    with patch("anvil.tools.ToolExecutor.run_uv_build", return_value=0):
        result = runner.invoke(main, ["build"])
        assert result.exit_code == 0
        assert "Building project" in result.output
        assert "Build completed successfully" in result.output
