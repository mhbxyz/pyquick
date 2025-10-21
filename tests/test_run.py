"""Tests for run command execution."""
from tomllib import load

import pytest
from unittest.mock import patch, MagicMock

from anvil.config import Config
from anvil.commands.run import RunExecutor


class TestRunExecutor:
    """Test RunExecutor functionality."""

    def test_executor_initialization(self):
        """Test executor initialization."""
        config = Config()
        executor = RunExecutor(config)
        assert executor.config == config

    @patch("anvil.commands.run.RunExecutor.run_command")
    def test_run_lib_profile_no_entry(self, mock_run_cmd):
        """Test running lib profile with no entry point."""
        config = Config()
        config.set("project.profile", "lib")
        config.set("project.package", "testlib")

        executor = RunExecutor(config)
        result = executor.run()

        # Should return 1 for lib with no entry
        assert result == 1
        mock_run_cmd.assert_not_called()

    @patch("anvil.commands.run.RunExecutor.run_command")
    def test_run_lib_profile_with_main(self, mock_run_cmd):
        """Test running lib profile with __main__.py."""
        mock_run_cmd.return_value = 0

        config = Config()
        config.set("project.profile", "lib")
        config.set("project.package", "testlib")

        executor = RunExecutor(config)

        # Mock that __main__.py exists
        with patch("pathlib.Path.exists", return_value=True):
            result = executor.run()
            assert result == 0
            mock_run_cmd.assert_called_with(["python", "-m", "testlib"])

    @patch("anvil.commands.run.RunExecutor.run_command")
    def test_run_cli_profile(self, mock_run_cmd):
        """Test running CLI profile."""
        mock_run_cmd.return_value = 0

        config = Config()
        config.set("project.profile", "cli")
        config.set("project.package", "testcli")

        executor = RunExecutor(config)

        with patch("pathlib.Path.exists", return_value=True):
            result = executor.run()
            assert result == 0
            mock_run_cmd.assert_called_with(["python", "-m", "testcli"])

    @patch("anvil.commands.run.RunExecutor.run_command")
    def test_run_api_profile_fastapi(self, mock_run_cmd):
        """Test running API profile with FastAPI."""
        mock_run_cmd.return_value = 0

        config = Config()
        config.set("project.profile", "api")
        config.set("project.package", "testapi")
        config.set("api.template", "fastapi")

        executor = RunExecutor(config)

        with patch.object(
            executor.executor.detector, "is_available", return_value=True
        ):
            result = executor.run()
            assert result == 0
            mock_run_cmd.assert_called_with(
                ["uvicorn", "testapi.app:app", "--host", "127.0.0.1", "--port", "8000"]
            )

    @patch("anvil.commands.run.RunExecutor.run_command")
    def test_run_api_profile_flask(self, mock_run_cmd):
        """Test running API profile with Flask."""
        mock_run_cmd.return_value = 0

        config = Config()
        config.set("project.profile", "api")
        config.set("project.package", "testapi")
        config.set("api.template", "flask")

        executor = RunExecutor(config)

        with patch.object(
            executor.executor.detector, "is_available", return_value=True
        ):
            result = executor.run()
            assert result == 0
            mock_run_cmd.assert_called_with(
                [
                    "flask",
                    "--app",
                    "testapi.app",
                    "run",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "5000",
                ]
            )

    def test_resolve_entry_point_run_entry(self):
        """Test resolving run.entry."""
        config = Config()
        config.set("run.entry", "myapp:app")

        executor = RunExecutor(config)
        result = executor._resolve_entry_point()

        assert result == [
            "uvicorn",
            "myapp:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]

    def test_resolve_entry_point_run_module(self):
        """Test resolving run.module."""
        config = Config()
        config.set("run.module", "myapp")

        executor = RunExecutor(config)
        result = executor._resolve_entry_point()

        assert result == ["python", "-m", "myapp"]

    @patch("pathlib.Path.exists")
    @patch("builtins.open")
    def test_resolve_entry_point_console_script(self, mock_open, mock_exists):
        """Test resolving console script from pyproject.toml."""
        mock_exists.return_value = True

        # Mock TOML content
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_open.return_value = mock_file

        with patch(
            "tomllib.load",
            return_value={"project": {"scripts": {"myscript": "myapp:main"}}},
        ):
            config = Config()
            executor = RunExecutor(config)
            result = executor._resolve_entry_point()

            assert result == ["myscript"]

    def test_resolve_app_entry_fastapi(self):
        """Test resolving FastAPI app entry."""
        config = Config()
        config.set("project.profile", "api")
        config.set("api.template", "fastapi")

        executor = RunExecutor(config)

        with patch.object(
            executor.executor.detector, "is_available", return_value=True
        ):
            result = executor._resolve_app_entry("myapp:app")
            assert result == [
                "uvicorn",
                "myapp:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ]

    def test_resolve_app_entry_flask(self):
        """Test resolving Flask app entry."""
        config = Config()
        config.set("project.profile", "api")
        config.set("api.template", "flask")

        executor = RunExecutor(config)

        with patch.object(
            executor.executor.detector, "is_available", side_effect=[False, True]
        ):
            result = executor._resolve_app_entry("myapp")
            assert result == [
                "flask",
                "--app",
                "myapp",
                "run",
                "--host",
                "127.0.0.1",
                "--port",
                "5000",
            ]
