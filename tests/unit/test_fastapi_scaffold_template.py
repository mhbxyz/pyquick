from pathlib import Path

from pyignite.scaffold import FastAPITemplateContext, build_fastapi_template, normalize_package_name


def test_normalize_package_name_handles_common_cases() -> None:
    assert normalize_package_name("my-api") == "my_api"
    assert normalize_package_name("  My API  ") == "my_api"
    assert normalize_package_name("123 service") == "app_123_service"
    assert normalize_package_name("!!!") == "app"


def test_fastapi_template_uses_project_named_package() -> None:
    context = FastAPITemplateContext.from_project_name("My API")
    files = build_fastapi_template(context)

    assert context.package_name == "my_api"
    assert Path("src/my_api/main.py") in files
    assert Path("src/my_api/api/router.py") in files
    assert Path("pyignite.toml") in files


def test_fastapi_template_sets_run_app_path_to_package_main() -> None:
    context = FastAPITemplateContext.from_project_name("billing-service")
    files = build_fastapi_template(context)

    pyignite_toml = files[Path("pyignite.toml")]
    assert 'app = "billing_service.main:app"' in pyignite_toml


def test_fastapi_template_does_not_include_db_dependencies_or_files() -> None:
    context = FastAPITemplateContext.from_project_name("myapi")
    files = build_fastapi_template(context)

    all_contents = "\n".join(files.values()).lower()
    assert "sqlalchemy" not in all_contents
    assert "alembic" not in all_contents
    assert "postgres" not in all_contents

    paths = {str(path) for path in files}
    assert "alembic.ini" not in paths
    assert "migrations" not in paths


def test_fastapi_template_contains_project_metadata_and_quality_defaults() -> None:
    context = FastAPITemplateContext.from_project_name("inventory-api")
    files = build_fastapi_template(context)

    pyproject = files[Path("pyproject.toml")]
    assert "fastapi" in pyproject
    assert "uvicorn" in pyproject
    assert "pytest" in pyproject
    assert "ruff" in pyproject
    assert "pyright" in pyproject


def test_fastapi_template_puts_application_python_code_under_src() -> None:
    context = FastAPITemplateContext.from_project_name("billing-api")
    files = build_fastapi_template(context)

    python_paths = [path for path in files if path.suffix == ".py"]
    app_python_paths = [path for path in python_paths if not str(path).startswith("tests/")]

    assert app_python_paths
    assert all(str(path).startswith("src/") for path in app_python_paths)
