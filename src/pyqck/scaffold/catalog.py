from __future__ import annotations

from pathlib import Path

from pyqck.scaffold.fastapi import FastAPITemplateContext, build_fastapi_template
from pyqck.scaffold.registry import ScaffoldRegistry


def build_default_scaffold_registry() -> ScaffoldRegistry:
    registry = ScaffoldRegistry()
    registry.register(
        profile="api",
        template="fastapi",
        generator=_build_api_fastapi,
        default=True,
    )

    registry.reserve_profile("lib")
    registry.reserve_profile("cli")
    registry.reserve_profile("web")
    registry.reserve_profile("game")
    return registry


def _build_api_fastapi(project_name: str) -> dict[Path, str]:
    context = FastAPITemplateContext.from_project_name(project_name)
    return build_fastapi_template(context)
