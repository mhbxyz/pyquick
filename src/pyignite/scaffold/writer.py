from __future__ import annotations

from pathlib import Path


def write_scaffold(destination: Path, files: dict[Path, str]) -> None:
    """Write scaffold files to destination deterministically."""

    for relative_path in sorted(files):
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(files[relative_path], encoding="utf-8")
