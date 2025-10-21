"""Tests for development mode functionality."""
from time import sleep
from pathlib import Path

import pytest
from unittest.mock import patch, MagicMock

from watchdog.observers import Observer

from anvil.config import Config
from anvil.tools import ToolExecutor
from anvil.commands.dev import DevRunner, DevEventHandler


class TestDevEventHandler:
    """Test DevEventHandler functionality."""

    def test_event_handler_initialization(self):
        """Test event handler initialization."""
        config = Config()
        executor = ToolExecutor(config)

        handler = DevEventHandler(config, executor)
        assert handler.config == config
        assert handler.executor == executor
        assert handler.debounce_ms == 150  # default value

    @patch("anvil.commands.dev.DevEventHandler._run_checks")
    def test_on_any_event_directory_ignored(self, mock_run_checks):
        """Test that directory events are ignored."""
        config = Config()
        executor = ToolExecutor(config)
        handler = DevEventHandler(config, executor)

        mock_event = MagicMock()
        mock_event.is_directory = True

        handler.on_any_event(mock_event)
        mock_run_checks.assert_not_called()

    @patch("anvil.commands.dev.DevEventHandler._run_checks")
    def test_on_any_event_pyc_ignored(self, mock_run_checks):
        """Test that .pyc files are ignored."""
        config = Config()
        executor = ToolExecutor(config)
        handler = DevEventHandler(config, executor)

        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/to/file.pyc"

        handler.on_any_event(mock_event)
        mock_run_checks.assert_not_called()

    @patch("anvil.commands.dev.DevEventHandler._run_checks")
    def test_on_any_event_debounced(self, mock_run_checks):
        """Test event debouncing."""
        config = Config()
        executor = ToolExecutor(config)
        handler = DevEventHandler(config, executor)

        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/path/to/file.py"

        # First event
        handler.on_any_event(mock_event)
        assert mock_run_checks.call_count == 1

        # Second event immediately after (should be debounced)
        handler.on_any_event(mock_event)
        assert mock_run_checks.call_count == 1

    @patch("anvil.commands.dev.ToolExecutor.run_ruff_check")
    @patch("anvil.commands.dev.ToolExecutor.run_ruff_format")
    @patch("anvil.commands.dev.ToolExecutor.run_pytest")
    def test_run_checks_all_pass(self, mock_pytest, mock_format, mock_lint):
        """Test running checks when all pass."""
        mock_lint.return_value = 0
        mock_format.return_value = 0
        mock_pytest.return_value = 0

        config = Config()
        executor = ToolExecutor(config)
        handler = DevEventHandler(config, executor)

        handler._run_checks()

        mock_lint.assert_called_with(["src", "tests"])
        mock_format.assert_called_with(["src", "tests"], check_only=True)
        mock_pytest.assert_called()


class TestDevRunner:
    """Test DevRunner functionality."""

    def test_runner_initialization(self):
        """Test runner initialization."""
        config = Config()
        executor = ToolExecutor(config)

        runner = DevRunner(config, executor)
        assert runner.config == config
        assert runner.executor == executor

    @patch("watchdog.observers.Observer")
    @patch("anvil.commands.dev.DevEventHandler")
    def test_run_lib_profile(self, mock_handler_class, mock_observer_class):
        """Test running dev mode for lib profile."""
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer

        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        config = Config()
        config.set("project.profile", "lib")
        config.set("dev.watch", ["src", "tests"])

        executor = ToolExecutor(config)
        runner = DevRunner(config, executor)

        # Mock Path.exists and is_dir
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=True),
            patch("time.sleep"),
        ):
            # Should not call _run_api_server for lib profile
            with patch.object(runner, "_run_api_server") as mock_api_server:
                runner.run()
                mock_api_server.assert_not_called()

            # Observer should be started and stopped
            mock_observer.start.assert_called_once()
            mock_observer.stop.assert_called_once()

    @patch("watchdog.observers.Observer")
    @patch("anvil.commands.dev.DevEventHandler")
    def test_run_api_profile(self, mock_handler_class, mock_observer_class):
        """Test running dev mode for API profile."""
        mock_observer = MagicMock()
        mock_observer_class.return_value = mock_observer

        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        config = Config()
        config.set("project.profile", "api")
        config.set("api.template", "fastapi")

        executor = ToolExecutor(config)
        runner = DevRunner(config, executor)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=True),
        ):
            with patch.object(runner, "_run_api_server") as mock_api_server:
                mock_api_server.return_value = None  # Prevent actual server start

                runner.run()

                # Should call API server for API profile
                mock_api_server.assert_called_once()

    @patch("anvil.commands.dev.ToolExecutor.run_command")
    def test_run_fastapi_server(self, mock_run_cmd):
        """Test running FastAPI server."""
        mock_run_cmd.return_value = 0

        config = Config()
        config.set("project.package", "testapi")

        executor = ToolExecutor(config)
        runner = DevRunner(config, executor)

        with patch.object(executor.detector, "is_available", return_value=True):
            runner._run_fastapi_server("testapi")

            mock_run_cmd.assert_called_with(
                [
                    "uvicorn",
                    "testapi.app:app",
                    "--reload",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ]
            )

    @patch("anvil.commands.dev.ToolExecutor.run_command")
    def test_run_flask_server(self, mock_run_cmd):
        """Test running Flask server."""
        mock_run_cmd.return_value = 0

        config = Config()
        config.set("project.package", "testapi")

        executor = ToolExecutor(config)
        runner = DevRunner(config, executor)

        with patch.object(executor.detector, "is_available", return_value=True):
            runner._run_flask_server("testapi")

            mock_run_cmd.assert_called_with(
                [
                    "flask",
                    "--app",
                    "testapi.app",
                    "run",
                    "--debug",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "5000",
                ]
            )

    def test_run_api_server_unknown_template(self):
        """Test API server with unknown template."""
        config = Config()
        config.set("project.profile", "api")
        config.set("api.template", "unknown")

        executor = ToolExecutor(config)
        runner = DevRunner(config, executor)

        # Should not raise exception, just log warning
        runner._run_api_server()
