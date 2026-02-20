from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Callable, Iterable, Sequence

import typer
from watchfiles import watch

from pyignite.tooling import ToolAdapters, ToolError, ToolKey

IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".pyright", ".venv", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}


def run_dev_loop(
    adapters: ToolAdapters,
    *,
    watch_factory: Callable[..., Iterable[set[tuple[object, str]]]] = watch,
    popen_factory: Callable[..., subprocess.Popen[bytes]] = subprocess.Popen,
) -> None:
    config = adapters.config
    watch_paths = [config.root_dir / relative_path for relative_path in config.dev.watch]

    running_args = (
        config.run.app,
        "--host",
        config.run.host,
        "--port",
        str(config.run.port),
    )

    running_command = adapters.command(ToolKey.RUNNING, args=running_args)

    typer.secho("Starting dev loop...", fg=typer.colors.CYAN)
    typer.secho(f"Watching: {', '.join(config.dev.watch)}", fg=typer.colors.CYAN)

    server_process = _start_server(
        command=running_command, cwd=config.root_dir, popen_factory=popen_factory
    )

    try:
        for changes in watch_factory(*watch_paths, debounce=config.dev.debounce_ms):
            changed_files = _filter_relevant_paths(changes=changes, root_dir=config.root_dir)
            if not changed_files:
                continue

            typer.secho(
                f"Change detected ({len(changed_files)} file(s)); reloading server and running checks.",
                fg=typer.colors.CYAN,
            )

            _stop_process(server_process)
            server_process = _start_server(
                command=running_command,
                cwd=config.root_dir,
                popen_factory=popen_factory,
            )

            _run_feedback_checks(adapters)
    except KeyboardInterrupt:
        typer.secho("Stopping dev loop...", fg=typer.colors.YELLOW)
    finally:
        _stop_process(server_process)


def _start_server(
    *,
    command: Sequence[str],
    cwd: Path,
    popen_factory: Callable[..., subprocess.Popen[bytes]],
) -> subprocess.Popen[bytes]:
    process = popen_factory(list(command), cwd=cwd)
    typer.secho(f"Server started: {' '.join(command)}", fg=typer.colors.GREEN)
    return process


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def _run_feedback_checks(adapters: ToolAdapters) -> None:
    pipeline = (
        ("lint", ToolKey.LINTING, ("check", ".")),
        ("type", ToolKey.TYPING, ()),
        ("test", ToolKey.TESTING, ()),
    )

    for step_name, tool_key, args in pipeline:
        typer.secho(f"Running [{step_name}]...", fg=typer.colors.CYAN)
        try:
            result = adapters.run(tool_key, args=args)
        except ToolError as exc:
            typer.secho(f"ERROR [tooling] {exc.message}", fg=typer.colors.RED, err=True)
            typer.secho(f"Hint: {exc.hint}", fg=typer.colors.YELLOW, err=True)
            return

        if result.stdout:
            typer.echo(result.stdout, nl=False)
        if result.stderr:
            typer.echo(result.stderr, err=True, nl=False)

        if result.exit_code == 0:
            typer.secho(f"OK [{step_name}]", fg=typer.colors.GREEN)
            continue

        typer.secho(
            f"FAILED [{step_name}] exit code {result.exit_code}", fg=typer.colors.RED, err=True
        )
        if adapters.config.checks.stop_on_first_failure:
            return


def _filter_relevant_paths(*, changes: set[tuple[object, str]], root_dir: Path) -> list[str]:
    selected: set[str] = set()
    for _, raw_path in changes:
        path = Path(raw_path)
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix in IGNORED_SUFFIXES:
            continue

        try:
            selected.add(str(path.relative_to(root_dir)))
        except ValueError:
            selected.add(str(path))

    return sorted(selected)
