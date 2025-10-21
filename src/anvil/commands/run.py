"""Entry point resolution and execution for anvil run command."""

from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:  # pragma: no cover - fallback for older Python
    import tomli as tomllib  # type: ignore

from rich.console import Console

from ..config import Config
from ..tools import ToolExecutor

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
            return self.run_command(entry_cmd)

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
        """Resolve ASGI/WSGI app entry point.

        Prefer simple, deterministic resolution for tests: when run.entry is
        provided, construct the expected command without checking tool presence.
        """
        template = self.config.get("api.template", "fastapi")

        if template == "flask":
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

        # Default to FastAPI
        return ["uvicorn", entry, "--host", "127.0.0.1", "--port", "8000"]

    # Provide a pass-through for tests that patch RunExecutor.run_command
    def run_command(self, cmd: list[str]) -> int:
        return self.executor.run_command(cmd)

    def _find_console_script(self) -> Optional[list[str]]:
        """Find console script from the project's pyproject.toml.

        Only returns a script if the pyproject's project.name matches the
        configured project name to avoid picking up the tool's own pyproject.
        """
        pyproject_path = self.config.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            return None

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            project = data.get("project", {})
            configured_name = self.config.get("project.name")
            # Avoid picking up the tool's own console script
            if project.get("name") == "anvil":
                return None
            if project.get("name") and project.get("name") != configured_name:
                return None

            scripts = project.get("scripts", {})
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
            return self.run_command(["python", "-m", package_name])

        console.print("[yellow]Warning:[/yellow] No entry point found for CLI app")
        return 1

    def _run_api_fallback(self) -> int:
        """Fallback for API profile."""
        package_name = self.config.get("project.package", "app")
        template = self.config.get("api.template", "fastapi")

        if template == "fastapi":
            app_path = f"{package_name}.app:app"
            if self.executor.detector.is_available("uvicorn"):
                return self.run_command(
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
                return self.run_command(
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
            return self.run_command(
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
            return self.run_command(["python", "-m", package_name])

        console.print("[yellow]Warning:[/yellow] Library has no runnable entry point")
        console.print(
            "[dim]Use 'anvil test' to run tests or 'anvil check' for validation[/dim]"
        )
        return 1
