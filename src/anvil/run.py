"""Entry point resolution and execution for anvil run command."""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console

from .config import Config
from .tools import ToolExecutor

console = Console()


class RunExecutor:
    """Handles execution of the canonical project entry point."""

    def __init__(self, config: Config):
        self.config = config
        self.executor = ToolExecutor(config)

    def run(self) -> int:
        """Run the project with the appropriate entry point."""
        profile = self.config.get("project.profile", "lib")

        # Try different entry point resolution strategies in order
        entry_cmd = self._resolve_entry_point()
        if entry_cmd:
            console.print(f"[dim]Running: {' '.join(entry_cmd)}[/dim]")
            return self.executor.run_command(entry_cmd)

        # Fallback based on profile
        if profile == "cli":
            return self._run_cli_fallback()
        elif profile == "api":
            return self._run_api_fallback()
        elif profile == "service":
            return self._run_service_fallback()
        else:
            return self._run_lib_fallback()

    def _resolve_entry_point(self) -> Optional[list[str]]:
        """Resolve the entry point using configuration."""
        # 1. Check for explicit run.entry (ASGI/WSGI app)
        entry = self.config.get("run.entry")
        if entry:
            return self._resolve_app_entry(entry)

        # 2. Check for run.module
        module = self.config.get("run.module")
        if module:
            return ["python", "-m", module]

        # 3. Check for console script in pyproject.toml
        script_cmd = self._find_console_script()
        if script_cmd:
            return script_cmd

        return None

    def _resolve_app_entry(self, entry: str) -> Optional[list[str]]:
        """Resolve ASGI/WSGI app entry point."""
        profile = self.config.get("project.profile", "lib")

        if profile == "api":
            template = self.config.get("api.template", "fastapi")
            if template == "fastapi":
                # Use uvicorn for FastAPI
                if self.executor.detector.is_available("uvicorn"):
                    return ["uvicorn", entry, "--host", "127.0.0.1", "--port", "8000"]
                else:
                    console.print(
                        "[yellow]Warning:[/yellow] uvicorn not available for FastAPI app"
                    )
            elif template == "flask":
                # Use gunicorn or flask for WSGI
                if self.executor.detector.is_available("gunicorn"):
                    return ["gunicorn", "--bind", "127.0.0.1:8000", entry]
                elif self.executor.detector.is_available("flask"):
                    return [
                        "flask",
                        "--app",
                        entry,
                        "run",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "5000",
                    ]
                else:
                    console.print(
                        "[yellow]Warning:[/yellow] No WSGI server available for Flask app"
                    )

        return None

    def _find_console_script(self) -> Optional[list[str]]:
        """Find console script from pyproject.toml."""
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            return None

        try:
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            scripts = data.get("project", {}).get("scripts", {})
            if scripts:
                # Use the first script found
                script_name = next(iter(scripts.keys()))
                return [script_name]

        except Exception:
            pass

        return None

    def _run_cli_fallback(self) -> int:
        """Fallback for CLI profile."""
        package_name = self.config.get("project.package", "app")

        # Try __main__.py
        main_file = Path("src") / package_name / "__main__.py"
        if main_file.exists():
            return self.executor.run_command(["python", "-m", package_name])

        console.print("[yellow]Warning:[/yellow] No entry point found for CLI app")
        return 1

    def _run_api_fallback(self) -> int:
        """Fallback for API profile."""
        package_name = self.config.get("project.package", "app")
        template = self.config.get("api.template", "fastapi")

        if template == "fastapi":
            app_path = f"{package_name}.app:app"
            if self.executor.detector.is_available("uvicorn"):
                return self.executor.run_command(
                    ["uvicorn", app_path, "--host", "127.0.0.1", "--port", "8000"]
                )
            else:
                console.print(
                    "[yellow]Warning:[/yellow] uvicorn not available for FastAPI"
                )
                return 1

        elif template == "flask":
            app_path = f"{package_name}.app"
            if self.executor.detector.is_available("flask"):
                return self.executor.run_command(
                    [
                        "flask",
                        "--app",
                        app_path,
                        "run",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "5000",
                    ]
                )
            else:
                console.print("[yellow]Warning:[/yellow] flask not available")
                return 1

        console.print(f"[yellow]Warning:[/yellow] Unknown API template '{template}'")
        return 1

    def _run_service_fallback(self) -> int:
        """Fallback for service profile."""
        package_name = self.config.get("project.package", "app")

        # Try service.py
        service_file = Path("src") / package_name / "service.py"
        if service_file.exists():
            return self.executor.run_command(
                ["python", "-m", f"{package_name}.service"]
            )

        console.print("[yellow]Warning:[/yellow] No service.py found")
        return 1

    def _run_lib_fallback(self) -> int:
        """Fallback for lib profile."""
        package_name = self.config.get("project.package", "app")

        # Try __main__.py for libraries that can be run
        main_file = Path("src") / package_name / "__main__.py"
        if main_file.exists():
            return self.executor.run_command(["python", "-m", package_name])

        console.print("[yellow]Warning:[/yellow] Library has no runnable entry point")
        console.print(
            "[dim]Use 'anvil test' to run tests or 'anvil check' for validation[/dim]"
        )
        return 1
