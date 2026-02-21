from pathlib import Path

import pytest

from pyqck.scaffold.catalog import build_default_scaffold_registry
from pyqck.scaffold.registry import (
    IncompatibleTemplateError,
    ReservedProfileError,
    ScaffoldRegistry,
    UnknownProfileError,
    UnknownTemplateError,
)


def _files(project_name: str) -> dict[Path, str]:
    return {Path("README.md"): f"# {project_name}\n"}


def test_registry_resolves_default_template_and_builds_files() -> None:
    registry = ScaffoldRegistry()
    registry.register(profile="api", template="fastapi", generator=_files, default=True)

    selection = registry.build(project_name="myapi", profile="api")

    assert selection.profile == "api"
    assert selection.template == "fastapi"
    assert selection.files[Path("README.md")] == "# myapi\n"


def test_registry_rejects_unknown_profile() -> None:
    registry = ScaffoldRegistry()
    registry.register(profile="api", template="fastapi", generator=_files, default=True)

    with pytest.raises(UnknownProfileError):
        registry.build(project_name="demo", profile="worker")


def test_registry_rejects_unknown_template_for_profile() -> None:
    registry = ScaffoldRegistry()
    registry.register(profile="api", template="fastapi", generator=_files, default=True)

    with pytest.raises(UnknownTemplateError):
        registry.build(project_name="demo", profile="api", template="flask")


def test_registry_rejects_incompatible_template_pair() -> None:
    registry = ScaffoldRegistry()
    registry.register(profile="api", template="fastapi", generator=_files, default=True)
    registry.register(profile="cli", template="baseline-cli", generator=_files, default=True)

    with pytest.raises(IncompatibleTemplateError):
        registry.build(project_name="demo", profile="cli", template="fastapi")


def test_default_registry_resolves_lib_profile() -> None:
    registry = build_default_scaffold_registry()

    selection = registry.build(project_name="mylib", profile="lib")

    assert selection.profile == "lib"
    assert selection.template == "baseline-lib"
    assert Path("pyproject.toml") in selection.files


def test_default_registry_marks_cli_as_reserved_profile() -> None:
    registry = build_default_scaffold_registry()

    with pytest.raises(ReservedProfileError):
        registry.build(project_name="demo", profile="cli")
