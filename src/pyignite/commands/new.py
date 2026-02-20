from __future__ import annotations

from pathlib import Path

import typer

from pyignite.scaffold import FastAPITemplateContext, build_fastapi_template
from pyignite.scaffold.writer import write_scaffold


def new_command(
    name: str = typer.Argument(..., help="Project directory name."),
    profile: str = typer.Option("api", "--profile", help="Project profile."),
    template: str = typer.Option("fastapi", "--template", help="Template to use."),
) -> None:
    """Create a new PyIgnite project scaffold."""

    if profile != "api":
        _usage_error("Unsupported profile.", "Use `--profile api` for v1.")
    if template != "fastapi":
        _usage_error("Unsupported template.", "Use `--template fastapi` for v1.")

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

    context = FastAPITemplateContext.from_project_name(name)
    files = build_fastapi_template(context)

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
        f"Created project `{name}` with profile `{profile}` and template `{template}`.",
        fg=typer.colors.GREEN,
    )
    typer.echo("Next steps:")
    typer.echo(f"  cd {name}")
    typer.echo("  uv sync")
    typer.echo("  uv run pyignite run")
    typer.echo("  uv run pyignite test")


def _usage_error(message: str, hint: str) -> None:
    typer.secho(f"ERROR [usage] {message}", fg=typer.colors.RED, err=True)
    typer.secho(f"Hint: {hint}", fg=typer.colors.YELLOW, err=True)
    raise typer.Exit(code=2)
