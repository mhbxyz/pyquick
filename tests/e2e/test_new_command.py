from pathlib import Path

from typer.testing import CliRunner

from pyqck.cli import app


def test_new_generates_fastapi_project_structure() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            ["new", "my-api", "--profile", "api", "--template", "fastapi"],
        )

        assert result.exit_code == 0
        assert "Created project `my-api`" in result.output
        assert "pyqck run" in result.output

        project_dir = Path("my-api")
        assert (project_dir / "pyquick.toml").exists()
        assert (project_dir / "src" / "my_api" / "main.py").exists()
        assert (project_dir / "src" / "my_api" / "api" / "health.py").exists()
        assert (project_dir / "tests" / "test_health.py").exists()

        pyquick_toml = (project_dir / "pyquick.toml").read_text(encoding="utf-8")
        assert 'app = "my_api.main:app"' in pyquick_toml


def test_new_rejects_non_empty_destination() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        project_dir = Path("myapi")
        project_dir.mkdir()
        (project_dir / "existing.txt").write_text("hello", encoding="utf-8")

        result = runner.invoke(app, ["new", "myapi", "--profile", "api", "--template", "fastapi"])

        assert result.exit_code == 2
        assert "ERROR [usage] Destination `myapi` already exists and is not empty." in result.output


def test_new_rejects_invalid_profile_or_template() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        invalid_profile = runner.invoke(app, ["new", "myapi", "--profile", "worker"])
        assert invalid_profile.exit_code == 2
        assert "ERROR [usage] Unsupported profile `worker`." in invalid_profile.output

        invalid_template = runner.invoke(app, ["new", "myapi", "--template", "flask"])
        assert invalid_template.exit_code == 2
        assert (
            "ERROR [usage] Unsupported template `flask` for profile `api`."
            in invalid_template.output
        )


def test_new_rejects_incompatible_profile_template_pair() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["new", "mycli", "--profile", "api", "--template", "baseline-cli"]
        )

        assert result.exit_code == 2
        assert (
            "ERROR [usage] Unsupported template `baseline-cli` for profile `api`." in result.output
        )
