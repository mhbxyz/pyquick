"""Main CLI entry point for Anvil."""

import os
import sys
from pathlib import Path
from typing import Optional

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
@click.option("--profile", default="lib", help="Project profile (lib, cli, api, service, monorepo)")
@click.option("--template", help="Template for API profile (fastapi, flask)")
def new(name: str, profile: str, template: str) -> None:
    """Scaffold a new Python project."""
    from .profiles import get_profile, list_profiles
    from .config import Config

    console.print(f"[bold green]🚀[/bold green] Creating new {profile} project: {name}")

    # Validate profile
    available_profiles = list_profiles()
    if profile not in available_profiles:
        console.print(f"[red]Error:[/red] Unknown profile '{profile}'. Available: {', '.join(available_profiles)}")
        return

    # Check if directory already exists
    project_dir = Path(name)
    if project_dir.exists():
        console.print(f"[red]Error:[/red] Directory '{name}' already exists")
        return

    # Create project directory
    project_dir.mkdir()
    os.chdir(project_dir)

    # Get profile and scaffold
    profile_obj = get_profile(profile)
    if profile_obj is None:
        console.print(f"[red]Error:[/red] Failed to load profile '{profile}'")
        return

    # Create initial config
    config = Config()
    config.set("project.name", name)
    config.set("project.package", name.replace("-", "_"))
    config.set("project.profile", profile)
    if template:
        config.set("api.template", template)

    # Scaffold project
    try:
        profile_obj.scaffold(name, config)
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
    console.print("[bold blue]👀[/bold blue] Starting development mode...")
    console.print("[yellow]Not implemented yet[/yellow]")


@main.command()
def run() -> None:
    """Run the canonical executable for the project."""
    console.print("[bold purple]▶️[/bold purple] Running project...")
    console.print("[yellow]Not implemented yet[/yellow]")


@main.command()
def fmt() -> None:
    """Format code using ruff."""
    console.print("[bold cyan]🎨[/bold cyan] Formatting code...")
    console.print("[yellow]Not implemented yet[/yellow]")


@main.command()
def lint() -> None:
    """Lint code using ruff."""
    console.print("[bold orange]🔍[/bold orange] Linting code...")
    console.print("[yellow]Not implemented yet[/yellow]")


@main.command()
def test() -> None:
    """Run tests using pytest."""
    console.print("[bold green]🧪[/bold green] Running tests...")
    console.print("[yellow]Not implemented yet[/yellow]")


@main.command()
def build() -> None:
    """Build the project using uv."""
    console.print("[bold magenta]📦[/bold magenta] Building project...")
    console.print("[yellow]Not implemented yet[/yellow]")


if __name__ == "__main__":
    main()