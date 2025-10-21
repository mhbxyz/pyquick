"""Main CLI entry point for Anvil."""

import os
from pathlib import Path

import click
from rich.console import Console

console = Console()


class AnvilGroup(click.Group):
    """Custom Click group with colored help output."""

    def get_help(self, ctx):
        """Override to provide colored help output."""
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.table import Table

        console = Console()

        # Create a colored help display
        console.print()  # Add spacing

        # Title
        title = Text("🔨 Anvil: Python Toolchain Orchestrator", style="bold cyan")
        console.print(Panel(title, border_style="cyan"))

        # Description
        desc = Text(
            "Scaffold, configure, and orchestrate Python projects with consistent tooling.\n"
            "Zero manual Makefiles, zero repetitive setup.",
            style="white",
        )
        console.print(desc)
        console.print()

        # Commands table
        table = Table(title="[bold green]Available Commands[/bold green]", box=None)
        table.add_column("Command", style="blue", no_wrap=True)
        table.add_column("Description", style="white")

        commands = [
            ("new", "Scaffold a new Python project"),
            ("dev", "Run project in development mode with watch"),
            ("run", "Run the canonical executable for the project"),
            ("fmt", "Format code"),
            ("lint", "Lint code"),
            ("check", "Run comprehensive code quality checks"),
            ("test", "Run tests"),
            ("build", "Build the project"),
            ("release", "Release the project"),
        ]

        for cmd_name, cmd_desc in commands:
            table.add_row(f"[bold blue]{cmd_name}[/bold blue]", cmd_desc)

        console.print(table)
        console.print()

        # Usage examples
        examples = Text("Examples:", style="bold yellow")
        console.print(examples)

        examples_table = Table(box=None, show_header=False)
        examples_table.add_column("", style="cyan")
        examples_table.add_column("", style="white")

        examples_data = [
            ("anvil new mylib", "Create a new library project"),
            (
                "anvil new myapi --profile api --template fastapi",
                "Create a FastAPI project",
            ),
            ("anvil dev", "Start development mode with auto-reload"),
            ("anvil check", "Run all quality checks"),
            ("anvil build", "Build wheel and source distributions"),
        ]

        for cmd, desc in examples_data:
            examples_table.add_row(f"  {cmd}", f"# {desc}")

        console.print(examples_table)
        console.print()

        # Footer
        footer = Text(
            "Run 'anvil COMMAND --help' for detailed help on a specific command.\n"
            "Version: 0.1.0",
            style="white",
        )
        console.print(footer)

        return ""  # Suppress default help output


@click.group(cls=AnvilGroup)
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


@main.command()
@click.option("--plan", is_flag=True, help="Show plan without applying changes")
@click.option("--force", is_flag=True, help="Apply changes without confirmation")
def apply(plan: bool, force: bool) -> None:
    """Apply anvil.toml configuration to project files."""
    from .config import Config
    from .patch import PatchEngine

    console.print("[bold purple]🔧[/bold purple] Applying configuration...")

    config = Config()
    engine = PatchEngine()

    if plan:
        # Show what would be changed
        operations = engine.plan_changes(config, config.project_root)

        if not operations:
            console.print("[dim]No changes needed - configuration is up to date[/dim]")
            return

        console.print(f"[bold]Planned changes ({len(operations)} operations):[/bold]")
        console.print()

        for i, op in enumerate(operations, 1):
            status_icon = {
                op.patch_type.value: "📄" if "file" in op.patch_type.value else "📦"
            }.get(op.patch_type.value, "🔧")

            console.print(f"{i}. {status_icon} {op.description}")
            console.print(f"   [dim]{op.patch_type.value}: {op.target_path}[/dim]")

        console.print()
        console.print("[green]✓[/green] Plan mode: no changes applied")
        console.print("[dim]Use --force to apply these changes[/dim]")
    else:
        # Apply the changes
        results = engine.apply_changes(
            config, config.project_root, force=force, dry_run=False
        )

        if not results:
            console.print("[dim]No changes applied - configuration is up to date[/dim]")
            return

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        console.print(f"[bold]Applied {len(successful)} changes:[/bold]")

        for result in successful:
            console.print(f"[green]✓[/green] {result.message}")

        if failed:
            console.print(f"[bold red]Failed {len(failed)} operations:[/bold red]")
            for result in failed:
                console.print(f"[red]✗[/red] {result.message}")

        if successful and not failed:
            console.print("[green]✓[/green] All changes applied successfully!")
        elif successful:
            console.print("[yellow]⚠️[/yellow] Some changes applied, some failed")
        else:
            console.print("[red]✗[/red] All changes failed")


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


@main.command()
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without doing it"
)
@click.option(
    "--patch", is_flag=True, help="Create patch file instead of applying changes"
)
@click.option("--force", is_flag=True, help="Force apply without confirmation")
def release(dry_run: bool, patch: bool, force: bool) -> None:
    """Release the project using commitizen and git tags."""
    from .config import Config
    from .tools import ToolExecutor

    console.print("[bold red]🚀[/bold red] Preparing release...")

    config = Config()
    executor = ToolExecutor(config)

    # Check if commitizen is available
    if not executor.detector.is_available("cz"):
        console.print("[red]Error:[/red] commitizen not available")
        console.print("[dim]Install with: uv add commitizen[/dim]")
        return

    # Check if we're in a git repository
    if not executor.detector.is_available("git"):
        console.print("[red]Error:[/red] git not available")
        return

    # Check git status
    if executor.run_command(["git", "status", "--porcelain"]) == 0:
        # No changes to commit
        console.print("[dim]Working directory is clean[/dim]")
    else:
        console.print(
            "[yellow]Warning:[/yellow] Working directory has uncommitted changes"
        )
        if not force:
            console.print("[dim]Use --force to continue anyway[/dim]")
            return

    # Run commitizen bump
    console.print("[dim]Running commitizen bump...[/dim]")
    bump_cmd = ["cz", "bump"]
    if dry_run:
        bump_cmd.append("--dry-run")
    elif patch:
        bump_cmd.extend(["--changelog", "--patch"])
    else:
        bump_cmd.append("--yes")

    exit_code = executor.run_command(bump_cmd)
    if exit_code != 0:
        console.print("[red]✗[/red] Release failed")
        return

    if dry_run:
        console.print("[green]✓[/green] Dry run completed")
        return

    console.print("[green]✓[/green] Release completed successfully!")
    console.print("[dim]Don't forget to push tags: git push --tags[/dim]")


if __name__ == "__main__":
    main()
