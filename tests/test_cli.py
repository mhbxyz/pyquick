"""Tests for CLI functionality."""

import pytest
from click.testing import CliRunner

from anvil.cli import main


def test_cli_help():
    """Test that CLI shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Anvil: Python toolchain orchestrator" in result.output


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


def test_dev_command():
    """Test dev command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["dev"])
    assert result.exit_code == 0
    assert "Starting development mode" in result.output
    assert "Not implemented yet" in result.output


def test_run_command():
    """Test run command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["run"])
    assert result.exit_code == 0
    assert "Running project" in result.output
    assert "Not implemented yet" in result.output


def test_fmt_command():
    """Test fmt command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["fmt"])
    assert result.exit_code == 0
    assert "Formatting code" in result.output
    assert "Not implemented yet" in result.output


def test_lint_command():
    """Test lint command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["lint"])
    assert result.exit_code == 0
    assert "Linting code" in result.output
    assert "Not implemented yet" in result.output


def test_test_command():
    """Test test command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["test"])
    assert result.exit_code == 0
    assert "Running tests" in result.output
    assert "Not implemented yet" in result.output


def test_build_command():
    """Test build command placeholder."""
    runner = CliRunner()
    result = runner.invoke(main, ["build"])
    assert result.exit_code == 0
    assert "Building project" in result.output
    assert "Not implemented yet" in result.output