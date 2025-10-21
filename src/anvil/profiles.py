"""Profile definitions and scaffolding logic for Anvil."""

from pathlib import Path
from typing import Dict, List, Optional

from .config import Config


class Profile:
    """Base class for project profiles."""

    def __init__(self, name: str, description: str):
        """Initialize profile.

        Args:
            name: Profile name
            description: Profile description
        """
        self.name = name
        self.description = description

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold project structure for this profile.

        Args:
            project_name: Name of the project
            config: Project configuration
        """
        raise NotImplementedError

    def generate_pyproject(self, project_name: str, config: Config) -> None:
        """Generate pyproject.toml for the project.

        Args:
            project_name: Name of the project
            config: Project configuration
        """
        from .pyproject import PyProjectGenerator

        generator = PyProjectGenerator(config)
        pyproject_path = config.project_root / "pyproject.toml"
        generator.write_to_file(pyproject_path)


class LibProfile(Profile):
    """Library profile for Python packages."""

    def __init__(self):
        super().__init__("lib", "Python library")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold library project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = config.project_root / "src"
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        (package_dir / "__init__.py").write_text(
            f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n'
        )

        # Create tests directory
        tests_dir = config.project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").write_text("")
        (tests_dir / "test_sanity.py").write_text(
            f'"""Basic tests for {package_name}."""\n\nimport {package_name}\n\n\ndef test_version():\n    """Test package version."""\n    assert {package_name}.__version__ == "0.1.0"\n'
        )


class CliProfile(Profile):
    """CLI application profile."""

    def __init__(self):
        super().__init__("cli", "CLI application")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold CLI project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = config.project_root / "src"
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py and __main__.py
        (package_dir / "__init__.py").write_text(
            f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n'
        )
        (package_dir / "__main__.py").write_text(
            f'"""Main entry point for {package_name}."""\n\n\ndef main():\n    """Main function."""\n    print("Hello from {package_name}!")\n\n\nif __name__ == "__main__":\n    main()\n'
        )


class ApiProfile(Profile):
    """Web API profile."""

    def __init__(self):
        super().__init__("api", "Web API")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold API project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))
        # Only scaffold specific frameworks when template is explicitly set.
        template = config.get("api.template")

        # Create src/package structure
        src_dir = config.project_root / "src"
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create basic API structure
        (package_dir / "__init__.py").write_text(
            f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n'
        )

        if template == "fastapi":
            self._scaffold_fastapi(package_name, package_dir)
        elif template == "flask":
            self._scaffold_flask(package_name, package_dir)
        else:
            # Default to basic structure
            (package_dir / "app.py").write_text(
                f'"""Application for {package_name}."""\n\n# Placeholder for app\n'
            )

    def _scaffold_fastapi(self, package_name: str, package_dir: Path) -> None:
        """Scaffold FastAPI application."""
        (package_dir / "app.py").write_text(
            f'''"""FastAPI application for {package_name}."""

from fastapi import FastAPI

app = FastAPI(title="{package_name}", version="0.1.0")

@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "Hello from {package_name}"}}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy"}}
'''
        )

        # Create main.py for running the app
        (package_dir / "__main__.py").write_text(
            f'''"""Main entry point for {package_name}."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("{package_name}.app:app", host="127.0.0.1", port=8000, reload=True)
'''
        )

    def _scaffold_flask(self, package_name: str, package_dir: Path) -> None:
        """Scaffold Flask application."""
        (package_dir / "app.py").write_text(
            f'''"""Flask application for {package_name}."""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def root():
    """Root endpoint."""
    return jsonify({{"message": "Hello from {package_name}"}})

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({{"status": "healthy"}})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
'''
        )


class ServiceProfile(Profile):
    """Background service profile."""

    def __init__(self):
        super().__init__("service", "Background service")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold service project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = config.project_root / "src"
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create service structure
        (package_dir / "__init__.py").write_text(
            f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n'
        )
        (package_dir / "service.py").write_text(
            f'"""Service implementation for {package_name}."""\n\n\ndef main():\n    """Main service function."""\n    print("Service {package_name} starting...")\n\n\nif __name__ == "__main__":\n    main()\n'
        )


class MonorepoProfile(Profile):
    """Monorepo workspace profile."""

    def __init__(self):
        super().__init__("monorepo", "Monorepo workspace")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold monorepo structure."""
        # Create packages directory
        packages_dir = config.project_root / "packages"
        packages_dir.mkdir(exist_ok=True)

        # Create basic workspace structure
        (packages_dir / "README.md").write_text(
            "# Packages\n\nThis directory contains workspace packages.\n"
        )


# Profile registry
PROFILES: Dict[str, Profile] = {
    "lib": LibProfile(),
    "cli": CliProfile(),
    "api": ApiProfile(),
    "service": ServiceProfile(),
    "monorepo": MonorepoProfile(),
}


def get_profile(name: str) -> Optional[Profile]:
    """Get profile by name.

    Args:
        name: Profile name

    Returns:
        Profile instance or None if not found
    """
    return PROFILES.get(name)


def list_profiles() -> List[str]:
    """List available profile names.

    Returns:
        List of profile names
    """
    return list(PROFILES.keys())
