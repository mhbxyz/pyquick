"""Pyproject.toml generation for Anvil projects."""

from pathlib import Path
from typing import Any, Dict

from .config import Config


class PyProjectGenerator:
    """Generates pyproject.toml files for different project profiles."""

    def __init__(self, config: Config):
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """Generate pyproject.toml content based on project configuration."""
        profile = self.config.get("project.profile", "lib")
        project_name = self.config.get("project.name", "myproject")
        package_name = self.config.get(
            "project.package", project_name.replace("-", "_")
        )
        python_version = self.config.get("project.python", "3.11")

        # Base project configuration
        pyproject = {
            "project": {
                "name": project_name,
                "version": "0.1.0",
                "description": f"A {profile} project",
                "readme": "README.md",
                "requires-python": f">={python_version}",
                "authors": [{"name": "Your Name", "email": "your.email@example.com"}],
                "keywords": ["python", profile],
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: MIT License",
                    "Programming Language :: Python :: 3",
                    f"Programming Language :: Python :: {python_version.replace('.', '')}",
                ],
                "dependencies": self._get_dependencies(profile),
            },
            "build-system": {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build",
            },
            "tool": {
                "hatch": {
                    "build": {
                        "targets": {"wheel": {"packages": [f"src/{package_name}"]}}
                    }
                }
            },
        }

        # Add profile-specific configuration
        if profile == "lib":
            pyproject = self._add_lib_config(pyproject, package_name)
        elif profile == "cli":
            pyproject = self._add_cli_config(pyproject, package_name, project_name)
        elif profile == "api":
            pyproject = self._add_api_config(pyproject, package_name)
        elif profile == "service":
            pyproject = self._add_service_config(pyproject, package_name)

        return pyproject

    def _get_dependencies(self, profile: str) -> list[str]:
        """Get base dependencies for the profile."""
        base_deps = []

        if profile == "api":
            template = self.config.get("api.template", "fastapi")
            if template == "fastapi":
                base_deps.extend(["fastapi>=0.100.0", "uvicorn[standard]>=0.20.0"])
            elif template == "flask":
                base_deps.extend(["flask>=2.0.0", "werkzeug>=2.0.0"])

        return base_deps

    def _add_lib_config(
        self, pyproject: Dict[str, Any], package_name: str
    ) -> Dict[str, Any]:
        """Add library-specific configuration."""
        # Add optional dependencies for development
        pyproject["project"]["optional-dependencies"] = {
            "dev": [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "ruff>=0.1.0",
                "mypy>=1.0.0",
                "pre-commit>=3.0.0",
            ]
        }

        # Add tool configurations
        pyproject["tool"]["ruff"] = {
            "line-length": 88,
            "target-version": "py311",
        }

        pyproject["tool"]["pytest"] = {
            "ini_options": {
                "testpaths": ["tests"],
                "python_files": ["test_*.py", "*_test.py"],
                "python_classes": ["Test*"],
                "python_functions": ["test_*"],
            }
        }

        return pyproject

    def _add_cli_config(
        self, pyproject: Dict[str, Any], package_name: str, project_name: str
    ) -> Dict[str, Any]:
        """Add CLI-specific configuration."""
        # Add console script
        pyproject["project"]["scripts"] = {
            project_name: f"{package_name}.__main__:main"
        }

        # Add same dev dependencies as lib
        pyproject["project"]["optional-dependencies"] = {
            "dev": [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "ruff>=0.1.0",
                "mypy>=1.0.0",
                "pre-commit>=3.0.0",
            ]
        }

        # Add tool configurations
        pyproject["tool"]["ruff"] = {
            "line-length": 88,
            "target-version": "py311",
        }

        return pyproject

    def _add_api_config(
        self, pyproject: Dict[str, Any], package_name: str
    ) -> Dict[str, Any]:
        """Add API-specific configuration."""
        # Add console script for running the API
        project_name = self.config.get("project.name", "myapi")
        template = self.config.get("api.template", "fastapi")

        if template == "fastapi":
            pyproject["project"]["scripts"] = {
                project_name: f"uvicorn {package_name}.app:app --host 127.0.0.1 --port 8000"
            }
        elif template == "flask":
            pyproject["project"]["scripts"] = {
                project_name: f"flask --app {package_name}.app run --host 127.0.0.1 --port 5000"
            }

        # Add dev dependencies
        pyproject["project"]["optional-dependencies"] = {
            "dev": [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "ruff>=0.1.0",
                "mypy>=1.0.0",
                "pre-commit>=3.0.0",
                "httpx>=0.24.0",  # For testing APIs
            ]
        }

        # Add tool configurations
        pyproject["tool"]["ruff"] = {
            "line-length": 88,
            "target-version": "py311",
        }

        return pyproject

    def _add_service_config(
        self, pyproject: Dict[str, Any], package_name: str
    ) -> Dict[str, Any]:
        """Add service-specific configuration."""
        # Add dev dependencies
        pyproject["project"]["optional-dependencies"] = {
            "dev": [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "ruff>=0.1.0",
                "mypy>=1.0.0",
                "pre-commit>=3.0.0",
            ]
        }

        # Add tool configurations
        pyproject["tool"]["ruff"] = {
            "line-length": 88,
            "target-version": "py311",
        }

        return pyproject

    def write_to_file(self, path: Path) -> None:
        """Write the generated pyproject.toml to a file."""
        pyproject_data = self.generate()

        # Simple TOML writer (could be improved with a proper TOML library)
        content = self._dict_to_toml(pyproject_data)
        path.write_text(content)

    def _dict_to_toml(self, data: Dict[str, Any], prefix: str = "") -> str:
        """Convert dictionary to TOML string (basic implementation)."""
        lines = []

        for key, value in data.items():
            if isinstance(value, dict):
                if prefix:
                    lines.append(f"\n[{prefix}.{key}]")
                else:
                    lines.append(f"\n[{key}]")
                lines.append(
                    self._dict_to_toml(value, f"{prefix}.{key}" if prefix else key)
                )
            elif isinstance(value, list):
                if prefix:
                    lines.append(f"\n[{prefix}.{key}]")
                else:
                    lines.append(f"\n[{key}]")
                for item in value:
                    if isinstance(item, str):
                        lines.append(f'"{item}",')
                    elif isinstance(item, dict):
                        # Handle array of tables
                        lines.append("")
                        for subkey, subvalue in item.items():
                            lines.append(f'{subkey} = "{subvalue}"')
                        lines.append("")
                    else:
                        lines.append(f"{item},")
            else:
                if isinstance(value, str):
                    lines.append(f'{key} = "{value}"')
                elif isinstance(value, bool):
                    lines.append(f"{key} = {str(value).lower()}")
                else:
                    lines.append(f"{key} = {value}")

        return "\n".join(lines)
