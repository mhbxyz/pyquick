"""Tool detection and execution utilities for Anvil."""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .config import Config

console = Console()


class ToolDetector:
    """Detects available development tools."""

    def __init__(self):
        self._cache = {}

    def is_available(self, tool: str) -> bool:
        """Check if a tool is available on the system.

        Args:
            tool: Tool name to check

        Returns:
            True if tool is available
        """
        if tool in self._cache:
            return self._cache[tool]

        available = shutil.which(tool) is not None
        self._cache[tool] = available
        return available

    def get_available_tools(self, tools: List[str]) -> List[str]:
        """Get list of available tools from a list of options.

        Args:
            tools: List of tool names to check

        Returns:
            List of available tools in preference order
        """
        return [tool for tool in tools if self.is_available(tool)]


class ToolExecutor:
    """Executes development tools with fallback behavior."""

    def __init__(self, config: Config):
        """Initialize tool executor.

        Args:
            config: Project configuration
        """
        self.config = config
        self.detector = ToolDetector()

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> int:
        """Run a command and return exit code.

        Args:
            command: Command to run as list of strings
            cwd: Working directory for command

        Returns:
            Exit code from command
        """
        try:
            result = subprocess.run(
                command,
                cwd=cwd or Path.cwd(),
                capture_output=False,  # Let output go to terminal
                text=True,
            )
            return result.returncode
        except FileNotFoundError:
            return 1
        except Exception:
            return 1

    def run_ruff_check(self, paths: List[str]) -> int:
        """Run ruff check (linting).

        Args:
            paths: Paths to check

        Returns:
            Exit code
        """
        if not self.detector.is_available("ruff"):
            return self._fallback_lint(paths)

        cmd = ["ruff", "check"] + paths
        return self.run_command(cmd)

    def run_ruff_format(self, paths: List[str], check_only: bool = False) -> int:
        """Run ruff format (formatting).

        Args:
            paths: Paths to format
            check_only: Only check formatting without modifying files

        Returns:
            Exit code
        """
        if not self.detector.is_available("ruff"):
            return self._fallback_format(paths, check_only)

        cmd = ["ruff", "format"]
        if check_only:
            cmd.append("--check")
        cmd.extend(paths)
        return self.run_command(cmd)

    def run_pytest(self, paths: Optional[List[str]] = None) -> int:
        """Run pytest.

        Args:
            paths: Test paths to run (optional)

        Returns:
            Exit code
        """
        if not self.detector.is_available("pytest"):
            return 1  # No fallback for testing

        cmd = ["pytest"]
        if paths:
            cmd.extend(paths)
        return self.run_command(cmd)

    def _fallback_lint(self, paths: List[str]) -> int:
        """Fallback linting when ruff is not available."""
        # Try flake8 as fallback
        if self.detector.is_available("flake8"):
            cmd = ["flake8"] + paths
            return self.run_command(cmd)

        # No linter available
        return 1

    def run_type_check(self) -> int:
        """Run type checking.

        Returns:
            Exit code
        """
        # Get preferred type checker from config
        type_checker = self.config.get("features.types", "pyright")

        if type_checker == "mypy":
            if self.detector.is_available("mypy"):
                cmd = ["mypy"]
                # Add common paths
                paths = self.config.get("lint.paths", ["src", "tests"])
                cmd.extend(paths)
                return self.run_command(cmd)
            else:
                console.print(
                    "[yellow]Warning:[/yellow] mypy not available, trying pyright..."
                )
                type_checker = "pyright"

        if type_checker == "pyright":
            if self.detector.is_available("pyright"):
                cmd = ["pyright"]
                return self.run_command(cmd)
            else:
                console.print(
                    "[yellow]Warning:[/yellow] pyright not available, trying mypy..."
                )
                if self.detector.is_available("mypy"):
                    cmd = ["mypy"]
                    paths = self.config.get("lint.paths", ["src", "tests"])
                    cmd.extend(paths)
                    return self.run_command(cmd)

        # No type checker available
        console.print("[yellow]Warning:[/yellow] No type checker available")
        return 1

    def _fallback_format(self, paths: List[str], check_only: bool) -> int:
        """Fallback formatting when ruff is not available."""
        # Try black as fallback
        if self.detector.is_available("black"):
            cmd = ["black"]
            if check_only:
                cmd.append("--check")
            cmd.extend(paths)
            return self.run_command(cmd)

        # No formatter available
        return 1

    def run_uv_build(self, wheel: bool = True, sdist: bool = True) -> int:
        """Run uv build to create distributions.

        Args:
            wheel: Build wheel distribution
            sdist: Build source distribution

        Returns:
            Exit code
        """
        if not self.detector.is_available("uv"):
            console.print(
                "[yellow]Warning:[/yellow] uv not available, trying python -m build"
            )
            if self.detector.is_available("python"):
                cmd = ["python", "-m", "build"]
                return self.run_command(cmd)
            else:
                console.print(
                    "[red]Error:[/red] Neither uv nor python available for building"
                )
                return 1

        cmd = ["uv", "build"]
        if not wheel:
            cmd.append("--no-wheel")
        if not sdist:
            cmd.append("--no-sdist")

        return self.run_command(cmd)
