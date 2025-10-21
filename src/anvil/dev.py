"""Development mode runner with file watching and auto-reload.

This module ensures that file watchers and background loops do not run
indefinitely in non-interactive environments (e.g., tests/CI). It detects
"one-shot" contexts and exits cleanly after initial checks, preventing thread
leaks and runaway memory usage when invoked under runners like Click's
CliRunner or pytest.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import Config
from .tools import ToolExecutor

console = Console()


class DevEventHandler(FileSystemEventHandler):
    """File system event handler for development mode."""

    def __init__(self, config: Config, executor: ToolExecutor):
        self.config = config
        self.executor = executor
        self.last_run = 0
        self.debounce_ms = config.get("dev.debounce_ms", 150)

    def on_any_event(self, event):
        """Handle file system events."""
        # Skip directory events and certain file types
        if event.is_directory:
            return

        # Skip common non-source files
        skip_patterns = {".pyc", ".pyo", "__pycache__", ".git", "node_modules"}
        path = Path(event.src_path)
        if any(pattern in str(path) for pattern in skip_patterns):
            return

        # Debounce rapid events
        current_time = time.time() * 1000
        if current_time - self.last_run < self.debounce_ms:
            return

        self.last_run = current_time
        self._run_checks()

    def _run_checks(self):
        """Run linting and testing checks."""
        console.print("\n[dim]🔍 Running checks...[/dim]")

        # Get paths from config
        lint_paths = self.config.get("lint.paths", ["src", "tests"])
        format_paths = self.config.get("format.paths", ["src", "tests"])

        # Run linting
        lint_exit_code = self.executor.run_ruff_check(lint_paths)
        if lint_exit_code == 0:
            console.print("  [green]✓[/green] Linting passed")
        else:
            console.print("  [red]✗[/red] Linting failed")

        # Run format check
        format_exit_code = self.executor.run_ruff_format(format_paths, check_only=True)
        if format_exit_code == 0:
            console.print("  [green]✓[/green] Formatting check passed")
        else:
            console.print("  [red]✗[/red] Formatting check failed")

        # Run tests, but avoid recursive invocation when the CLI dev command
        # is invoked under pytest (prevents nested pytest processes).
        if os.environ.get("ANVIL_FROM_CLI_DEV") and os.environ.get(
            "PYTEST_CURRENT_TEST"
        ):
            console.print("  [dim]Skipping pytest (running inside pytest)[/dim]")
            test_exit_code = 0
        else:
            test_exit_code = self.executor.run_pytest()
        if test_exit_code == 0:
            console.print("  [green]✓[/green] Tests passed")
        else:
            console.print("  [red]✗[/red] Tests failed")


class DevRunner:
    """Development mode runner."""

    def __init__(self, config: Config, executor: ToolExecutor):
        self.config = config
        self.executor = executor

    def run(self) -> None:
        """Run development mode."""
        # Determine whether to run in one-shot mode (no infinite loop / server).
        # Heuristics:
        # - Explicit opt-in via env var `ANVIL_DEV_ONESHOT`.
        # - Non-interactive stdio (common under tests/CI and Click's CliRunner).
        oneshot = bool(os.environ.get("ANVIL_DEV_ONESHOT")) or not (
            hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        )

        # Get watch paths from config
        watch_paths = self.config.get("dev.watch", ["src", "tests"])
        profile = self.config.get("project.profile", "lib")

        # Convert to Path objects and ensure they exist
        watch_dirs = []
        for path_str in watch_paths:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                watch_dirs.append(path)
            else:
                console.print(
                    f"[yellow]Warning:[/yellow] Watch path '{path_str}' not found, skipping"
                )

        if not watch_dirs:
            console.print("[red]Error:[/red] No valid watch directories found")
            return

        # Set up file watcher
        observer = Observer()
        event_handler = DevEventHandler(self.config, self.executor)

        for watch_dir in watch_dirs:
            observer.schedule(event_handler, str(watch_dir), recursive=True)
            console.print(f"[dim]Watching: {watch_dir}[/dim]")

        observer.start()

        try:
            # Run initial checks
            console.print("[dim]Running initial checks...[/dim]")
            event_handler._run_checks()

            # For API profiles, also attempt to start the server with auto-reload
            if profile == "api":
                self._run_api_server()

            # Short-circuit in one-shot mode to avoid infinite loops/threads
            if oneshot:
                return

            # For other profiles, just watch and run checks
            console.print("[dim]Press Ctrl+C to stop...[/dim]")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            # Always stop and join observer to prevent thread leaks
            try:
                observer.stop()
            finally:
                observer.join()

    def _run_api_server(self) -> None:
        """Run API server with auto-reload for API profiles."""
        # Respect one-shot environments to avoid long-lived processes in tests/CI
        if os.environ.get("ANVIL_DEV_ONESHOT") or not (
            hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        ):
            return
        template = self.config.get("api.template", "fastapi")
        package_name = self.config.get("project.package", "app")

        if template == "fastapi":
            self._run_fastapi_server(package_name)
        elif template == "flask":
            self._run_flask_server(package_name)
        else:
            console.print(
                f"[yellow]Warning:[/yellow] Unknown API template '{template}', falling back to watch mode"
            )
            if os.environ.get("ANVIL_DEV_ONESHOT") or not (
                hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
            ):
                return
            console.print("[dim]Press Ctrl+C to stop...[/dim]")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

    def _run_fastapi_server(self, package_name: str) -> None:
        """Run FastAPI server with uvicorn."""
        if not self.executor.detector.is_available("uvicorn"):
            console.print(
                "[yellow]Warning:[/yellow] uvicorn not available, install with: uv add uvicorn"
            )
            return

        console.print(f"[dim]Starting FastAPI server for {package_name}...[/dim]")
        app_path = f"{package_name}.app:app"

        # Run uvicorn with reload
        cmd = ["uvicorn", app_path, "--reload", "--host", "127.0.0.1", "--port", "8000"]
        exit_code = self.executor.run_command(cmd)

        if exit_code != 0:
            console.print("[red]Error:[/red] Failed to start FastAPI server")

    def _run_flask_server(self, package_name: str) -> None:
        """Run Flask server with development mode."""
        if not self.executor.detector.is_available("flask"):
            console.print(
                "[yellow]Warning:[/yellow] flask not available, install with: uv add flask"
            )
            return

        console.print(f"[dim]Starting Flask server for {package_name}...[/dim]")
        app_path = f"{package_name}.app"

        # Run flask with development mode
        cmd = [
            "flask",
            "--app",
            app_path,
            "run",
            "--debug",
            "--host",
            "127.0.0.1",
            "--port",
            "5000",
        ]
        exit_code = self.executor.run_command(cmd)

        if exit_code != 0:
            console.print("[red]Error:[/red] Failed to start Flask server")
