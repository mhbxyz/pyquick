from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ScaffoldGenerator = Callable[[str], dict[Path, str]]


@dataclass(slots=True, frozen=True)
class ScaffoldSelection:
    profile: str
    template: str
    files: dict[Path, str]


@dataclass(slots=True, frozen=True)
class TemplateRegistration:
    generator: ScaffoldGenerator
    is_default: bool = False


class ScaffoldLookupError(ValueError):
    def __init__(self, message: str, hint: str) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


class UnknownProfileError(ScaffoldLookupError):
    def __init__(self, profile: str, available_profiles: tuple[str, ...]) -> None:
        hint = f"Use one of: {', '.join(available_profiles)}."
        super().__init__(f"Unsupported profile `{profile}`.", hint)


class ReservedProfileError(ScaffoldLookupError):
    def __init__(self, profile: str) -> None:
        super().__init__(
            f"Profile `{profile}` is reserved and not scaffoldable yet.",
            "Use `--profile api --template fastapi` until this profile ships.",
        )


class UnknownTemplateError(ScaffoldLookupError):
    def __init__(self, template: str, profile: str, available_templates: tuple[str, ...]) -> None:
        hint = f"Use one of: {', '.join(available_templates)} for profile `{profile}`."
        super().__init__(f"Unsupported template `{template}` for profile `{profile}`.", hint)


class IncompatibleTemplateError(ScaffoldLookupError):
    def __init__(self, profile: str, template: str) -> None:
        super().__init__(
            f"Template `{template}` is not compatible with profile `{profile}`.",
            "Choose a template from the selected profile's template catalog.",
        )


class ScaffoldRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, TemplateRegistration]] = {}
        self._reserved_profiles: set[str] = set()

    def register(
        self,
        *,
        profile: str,
        template: str,
        generator: ScaffoldGenerator,
        default: bool = False,
    ) -> None:
        profile_templates = self._templates.setdefault(profile, {})
        profile_templates[template] = TemplateRegistration(generator=generator, is_default=default)
        self._reserved_profiles.discard(profile)

        if default:
            for name, registration in list(profile_templates.items()):
                if name == template:
                    continue
                profile_templates[name] = TemplateRegistration(
                    generator=registration.generator,
                    is_default=False,
                )

    def reserve_profile(self, profile: str) -> None:
        if profile in self._templates:
            return
        self._reserved_profiles.add(profile)

    def build(
        self, *, project_name: str, profile: str, template: str | None = None
    ) -> ScaffoldSelection:
        if profile in self._reserved_profiles:
            raise ReservedProfileError(profile)

        if profile not in self._templates:
            available_profiles = tuple(sorted((*self._templates.keys(), *self._reserved_profiles)))
            raise UnknownProfileError(profile, available_profiles=available_profiles)

        profile_templates = self._templates[profile]
        resolved_template = template or self._default_template_for(profile)

        if resolved_template not in profile_templates:
            if self._template_exists_anywhere(resolved_template):
                raise IncompatibleTemplateError(profile=profile, template=resolved_template)
            available_templates = tuple(sorted(profile_templates.keys()))
            raise UnknownTemplateError(
                resolved_template,
                profile=profile,
                available_templates=available_templates,
            )

        files = profile_templates[resolved_template].generator(project_name)
        return ScaffoldSelection(profile=profile, template=resolved_template, files=files)

    def _default_template_for(self, profile: str) -> str:
        for template_name, registration in self._templates[profile].items():
            if registration.is_default:
                return template_name

        raise ScaffoldLookupError(
            f"No default template configured for profile `{profile}`.",
            "Register a default template for this profile in the scaffold registry.",
        )

    def _template_exists_anywhere(self, template: str) -> bool:
        for templates in self._templates.values():
            if template in templates:
                return True
        return False
