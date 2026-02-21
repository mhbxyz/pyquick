from __future__ import annotations

from pathlib import Path

import typer

from pyqck.scaffold import ScaffoldLookupError, build_default_scaffold_registry
from pyqck.scaffold.writer import write_scaffold


def new_command(
    name: str = typer.Argument(..., help="Project directory name."),
    profile: str = typer.Option("api", "--profile", help="Project profile."),
    template: str | None = typer.Option(None, "--template", help="Template to use."),
) -> None:
    """Create a new PyQuick project scaffold."""

    registry = build_default_scaffold_registry()
    try:
        selection = registry.build(project_name=name, profile=profile, template=template)
    except ScaffoldLookupError as exc:
        _usage_error(exc.message, exc.hint)

    destination = Path.cwd() / name
    if destination.exists() and not destination.is_dir():
        _usage_error(
            f"Destination `{destination.name}` exists and is not a directory.",
            "Choose a different project name.",
        )
    if destination.exists() and any(destination.iterdir()):
        _usage_error(
            f"Destination `{destination.name}` already exists and is not empty.",
            "Choose a new directory name or empty the destination first.",
        )

    files = selection.files

    try:
        destination.mkdir(parents=True, exist_ok=True)
        write_scaffold(destination=destination, files=files)
    except OSError as exc:
        typer.secho(
            f"ERROR [tooling] Could not generate project `{name}`.",
            fg=typer.colors.RED,
            err=True,
        )
        typer.secho(
            f"Hint: Check filesystem permissions and free space ({exc}).",
            fg=typer.colors.YELLOW,
            err=True,
        )
        raise typer.Exit(code=1) from exc

    typer.secho(
        (
            f"Created project `{name}` with profile `{selection.profile}` "
            f"and template `{selection.template}`."
        ),
        fg=typer.colors.GREEN,
    )
    typer.echo("Next steps:")
    typer.echo(f"  cd {name}")
    typer.echo("  pyqck install")
    typer.echo("  pyqck run")
    typer.echo("  pyqck test")


def _usage_error(message: str, hint: str) -> None:
    typer.secho(f"ERROR [usage] {message}", fg=typer.colors.RED, err=True)
    typer.secho(f"Hint: {hint}", fg=typer.colors.YELLOW, err=True)
    raise typer.Exit(code=2)
