from pathlib import Path

from pyqck.scaffold import LibTemplateContext, build_lib_template


def test_lib_template_builds_expected_layout() -> None:
    context = LibTemplateContext.from_project_name("My Library")
    files = build_lib_template(context)

    assert Path("pyproject.toml") in files
    assert Path("pyquick.toml") in files
    assert Path("src/my_library/__init__.py") in files
    assert Path("tests/test_my_library.py") in files


def test_lib_template_uses_lib_profile_and_default_template() -> None:
    context = LibTemplateContext.from_project_name("billing-lib")
    files = build_lib_template(context)

    pyquick_toml = files[Path("pyquick.toml")]
    assert 'profile = "lib"' in pyquick_toml
    assert 'template = "baseline-lib"' in pyquick_toml


def test_lib_template_contains_quality_defaults() -> None:
    context = LibTemplateContext.from_project_name("billing-lib")
    files = build_lib_template(context)

    pyproject = files[Path("pyproject.toml")]
    assert '"pytest>=8.3.0"' in pyproject
    assert '"ruff>=0.8.0"' in pyproject
    assert '"pyright>=1.1.390"' in pyproject


def test_lib_template_generates_importable_baseline_test() -> None:
    context = LibTemplateContext.from_project_name("billing-lib")
    files = build_lib_template(context)

    test_module = files[Path("tests/test_billing_lib.py")]
    assert "from billing_lib import add" in test_module
    assert "assert add(2, 3) == 5" in test_module
