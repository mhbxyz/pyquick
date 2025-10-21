"""Profile definitions and scaffolding logic for Anvil."""

import os
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


class LibProfile(Profile):
    """Library profile for Python packages."""

    def __init__(self):
        super().__init__("lib", "Python library")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold library project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = Path("src")
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        (package_dir / "__init__.py").write_text(f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n')

        # Create tests directory
        tests_dir = Path("tests")
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").write_text("")
        (tests_dir / "test_sanity.py").write_text(f'"""Basic tests for {package_name}."""\n\nimport {package_name}\n\n\ndef test_version():\n    """Test package version."""\n    assert {package_name}.__version__ == "0.1.0"\n')


class CliProfile(Profile):
    """CLI application profile."""

    def __init__(self):
        super().__init__("cli", "CLI application")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold CLI project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = Path("src")
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py and __main__.py
        (package_dir / "__init__.py").write_text(f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n')
        (package_dir / "__main__.py").write_text(f'"""Main entry point for {package_name}."""\n\n\ndef main():\n    """Main function."""\n    print("Hello from {package_name}!")\n\n\nif __name__ == "__main__":\n    main()\n')


class ApiProfile(Profile):
    """Web API profile."""

    def __init__(self):
        super().__init__("api", "Web API")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold API project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = Path("src")
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create basic API structure
        (package_dir / "__init__.py").write_text(f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n')
        (package_dir / "app.py").write_text(f'"""FastAPI application for {package_name}."""\n\n# Placeholder for FastAPI app\n')


class ServiceProfile(Profile):
    """Background service profile."""

    def __init__(self):
        super().__init__("service", "Background service")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold service project structure."""
        package_name = config.get("project.package", project_name.replace("-", "_"))

        # Create src/package structure
        src_dir = Path("src")
        package_dir = src_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create service structure
        (package_dir / "__init__.py").write_text(f'"""Package {package_name}."""\n\n__version__ = "0.1.0"\n')
        (package_dir / "service.py").write_text(f'"""Service implementation for {package_name}."""\n\n\ndef main():\n    """Main service function."""\n    print("Service {package_name} starting...")\n\n\nif __name__ == "__main__":\n    main()\n')


class MonorepoProfile(Profile):
    """Monorepo workspace profile."""

    def __init__(self):
        super().__init__("monorepo", "Monorepo workspace")

    def scaffold(self, project_name: str, config: Config) -> None:
        """Scaffold monorepo structure."""
        # Create packages directory
        packages_dir = Path("packages")
        packages_dir.mkdir(exist_ok=True)

        # Create basic workspace structure
        (packages_dir / "README.md").write_text("# Packages\n\nThis directory contains workspace packages.\n")


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