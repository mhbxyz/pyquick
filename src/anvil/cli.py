"""Main CLI entry point for Anvil."""

import os
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Anvil: Python toolchain orchestrator.

    Scaffold, configure, and orchestrate Python projects with consistent tooling.
    """
    pass


@main.command()
@click.argument("name")
@click.option(
    "--profile",
    default="lib",
    help="Project profile (lib, cli, api, service, monorepo)",
)
@click.option("--template", help="Template for API profile (fastapi, flask)")
def new(name: str, profile: str, template: str) -> None:
    """Scaffold a new Python project."""
    from .profiles import get_profile, list_profiles
    from .config import Config

    console.print(f"[bold green]🚀[/bold green] Creating new {profile} project: {name}")

    # Validate profile
    available_profiles = list_profiles()
    if profile not in available_profiles:
        console.print(
            f"[red]Error:[/red] Unknown profile '{profile}'. Available: {', '.join(available_profiles)}"
        )
        return

    # Check if directory already exists
    project_dir = Path(name)
    if project_dir.exists():
        console.print(f"[red]Error:[/red] Directory '{name}' already exists")
        return

    # Create project directory (do not change global CWD)
    project_dir.mkdir()

    # Get profile and scaffold
    profile_obj = get_profile(profile)
    if profile_obj is None:
        console.print(f"[red]Error:[/red] Failed to load profile '{profile}'")
        return

    # Create initial config anchored to the new project directory and load defaults
    config = Config(project_dir)
    config.load()
    config.set("project.name", name)
    config.set("project.package", name.replace("-", "_"))
    config.set("project.profile", profile)
    if template:
        config.set("api.template", template)

    # Scaffold project
    try:
        profile_obj.scaffold(name, config)
        profile_obj.generate_pyproject(name, config)
        config.save()
        console.print(f"[green]✓[/green] Project '{name}' created successfully!")
        console.print(f"[dim]Profile: {profile}[/dim]")
        console.print(f"[dim]Next: cd {name} && anvil dev[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to scaffold project: {e}")
        return


@main.command()
def dev() -> None:
    """Run project in development mode with watch."""
    from .config import Config
    from .tools import ToolExecutor
    from .commands.dev import DevRunner

    console.print("[bold blue]👀[/bold blue] Starting development mode...")

    config = Config()
    executor = ToolExecutor(config)
    dev_runner = DevRunner(config, executor)

    # Signal to dev runner that we're executing via CLI to avoid nested pytest
    prev_flag = os.environ.get("ANVIL_FROM_CLI_DEV")
    os.environ["ANVIL_FROM_CLI_DEV"] = "1"
    try:
        dev_runner.run()
    except KeyboardInterrupt:
        console.print("\n[dim]Development mode stopped.[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to start development mode: {e}")
        return
    finally:
        # Restore previous env
        if prev_flag is None:
            os.environ.pop("ANVIL_FROM_CLI_DEV", None)
        else:
            os.environ["ANVIL_FROM_CLI_DEV"] = prev_flag


@main.command()
def run() -> None:
    """Run the canonical executable for the project."""
    from .config import Config
    # Use absolute import to avoid any ambiguity with relative imports
    # inside Click invocation contexts.
    from .commands.run import RunExecutor

    console.print("[bold purple]▶️[/bold purple] Running project...")

    config = Config()
    run_executor = RunExecutor(config)

    try:
        exit_code = run_executor.run()
        if exit_code != 0:
            console.print(
                f"[red]Error:[/red] Command failed with exit code {exit_code}"
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to run project: {e}")


@main.command()
@click.option("--check", is_flag=True, help="Check formatting without modifying files")
def fmt(check: bool) -> None:
    """Format code using ruff."""
    from .config import Config
    from .tools import ToolExecutor

    console.print("[bold cyan]🎨[/bold cyan] Formatting code...")

    config = Config()
    executor = ToolExecutor(config)

    # Get paths from config or default to common paths
    paths = config.get("format.paths", ["src", "tests"])

    exit_code = executor.run_ruff_format(paths, check_only=check)

    if exit_code == 0:
        if check:
            console.print("[green]✓[/green] Code is properly formatted")
        else:
            console.print("[green]✓[/green] Code formatted successfully")
    else:
        if check:
            console.print("[red]✗[/red] Code formatting issues found")
        else:
            console.print("[red]✗[/red] Formatting failed")


@main.command()
def lint() -> None:
    """Lint code using ruff."""
    from .config import Config
    from .tools import ToolExecutor

    console.print("[bold orange]🔍[/bold orange] Linting code...")

    config = Config()
    executor = ToolExecutor(config)

    # Get paths from config or default to common paths
    paths = config.get("lint.paths", ["src", "tests"])

    exit_code = executor.run_ruff_check(paths)

    if exit_code == 0:
        console.print("[green]✓[/green] No linting issues found")
    else:
        console.print("[red]✗[/red] Linting issues found")


@main.command()
def check() -> None:
    """Run comprehensive code quality checks (lint + fmt --check + type-check)."""
    from .config import Config
    from .tools import ToolExecutor

    console.print("[bold blue]🔍[/bold blue] Running comprehensive code checks...")

    config = Config()
    executor = ToolExecutor(config)

    # Get paths from config or default to common paths
    lint_paths = config.get("lint.paths", ["src", "tests"])
    format_paths = config.get("format.paths", ["src", "tests"])

    all_passed = True

    # Run linting
    console.print("  [dim]Running linter...[/dim]")
    lint_exit_code = executor.run_ruff_check(lint_paths)
    if lint_exit_code == 0:
        console.print("  [green]✓[/green] Linting passed")
    else:
        console.print("  [red]✗[/red] Linting failed")
        all_passed = False

    # Run format check
    console.print("  [dim]Checking formatting...[/dim]")
    format_exit_code = executor.run_ruff_format(format_paths, check_only=True)
    if format_exit_code == 0:
        console.print("  [green]✓[/green] Formatting check passed")
    else:
        console.print("  [red]✗[/red] Formatting check failed")
        all_passed = False

    # Run type checking only if explicitly enabled (boolean or dict flag).
    # This avoids accidentally running heavy type checkers during tests
    # when users set a string like "pyright" as the tool preference.
    types_setting = config.get("features.types", False)
    types_enabled = (
        (isinstance(types_setting, bool) and types_setting is True)
        or (
            isinstance(types_setting, dict)
            and bool(types_setting.get("enabled", False))
        )
    )

    if types_enabled:
        console.print("  [dim]Running type checker...[/dim]")
        type_exit_code = executor.run_type_check()
        if type_exit_code == 0:
            console.print("  [green]✓[/green] Type checking passed")
        else:
            console.print("  [red]✗[/red] Type checking failed")
            all_passed = False
    else:
        console.print("  [dim]Type checking skipped (not enabled)[/dim]")

    if all_passed:
        console.print("[green]✓[/green] All checks passed!")
    else:
        console.print("[red]✗[/red] Some checks failed")


@main.command()
def test() -> None:
    """Run tests using pytest."""
    from .config import Config
    from .tools import ToolExecutor

    console.print("[bold green]🧪[/bold green] Running tests...")

    config = Config()
    executor = ToolExecutor(config)

    # For now, run pytest without specific paths (it will find tests automatically)
    exit_code = executor.run_pytest()

    if exit_code == 0:
        console.print("[green]✓[/green] All tests passed")
    else:
        console.print("[red]✗[/red] Some tests failed")


@main.command()
@click.option("--wheel", is_flag=True, help="Build wheel distribution")
@click.option("--sdist", is_flag=True, help="Build source distribution")
def build(wheel: bool, sdist: bool) -> None:
    """Build the project using uv."""
    from .config import Config
    from .tools import ToolExecutor

    console.print("[bold magenta]📦[/bold magenta] Building project...")

    config = Config()
    executor = ToolExecutor(config)

    # Default to building both if neither specified
    if not wheel and not sdist:
        wheel = sdist = True

    exit_code = executor.run_uv_build(wheel=wheel, sdist=sdist)

    if exit_code == 0:
        console.print("[green]✓[/green] Build completed successfully")
        console.print("[dim]Distributions created in dist/ directory[/dim]")
    else:
        console.print("[red]✗[/red] Build failed")


if __name__ == "__main__":
    main()
