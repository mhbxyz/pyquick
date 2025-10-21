"""Configuration validation for Anvil."""

from typing import Any, List, Optional
import re

from .config import Config


class ValidationError(Exception):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(f"{field}: {message}" if field else message)


class ValidationWarning:
    """Represents a validation warning."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.field = field
        self.suggestion = suggestion

    def __str__(self) -> str:
        msg = f"Warning: {self.message}"
        if self.field:
            msg = f"{self.field}: {msg}"
        if self.suggestion:
            msg += f" (Suggestion: {self.suggestion})"
        return msg


class ConfigValidator:
    """Validates Anvil configuration files."""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []

    def validate(self, config: Config) -> bool:
        """Validate the entire configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        self.errors.clear()
        self.warnings.clear()

        try:
            # Load config if not already loaded
            if not config._config:
                config.load()

            self._validate_project_section(config)
            self._validate_features_section(config)
            self._validate_tooling_section(config)
            self._validate_paths_section(config)
            self._validate_ci_section(config)

        except Exception as e:
            self.errors.append(ValidationError(f"Configuration loading failed: {e}"))

        return len(self.errors) == 0

    def _validate_project_section(self, config: Config) -> None:
        """Validate the [project] section."""
        project = config.get("project", {})

        # Required fields
        required_fields = ["name", "package", "profile"]
        for field in required_fields:
            if field not in project:
                self.errors.append(
                    ValidationError(
                        f"Required field '{field}' is missing", f"project.{field}"
                    )
                )

        # Name validation
        name = project.get("name")
        if name:
            if not isinstance(name, str):
                self.errors.append(ValidationError("Must be a string", "project.name"))
            elif not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
                self.errors.append(
                    ValidationError(
                        "Invalid project name format. Use only letters, numbers, hyphens, and underscores. Must start with a letter",
                        "project.name",
                    )
                )

        # Package validation
        package = project.get("package")
        if package:
            if not isinstance(package, str):
                self.errors.append(
                    ValidationError("Must be a string", "project.package")
                )
            elif not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", package):
                self.errors.append(
                    ValidationError(
                        "Invalid package name format. Use only letters, numbers, and underscores. Must start with a letter",
                        "project.package",
                    )
                )

        # Profile validation
        profile = project.get("profile")
        if profile:
            valid_profiles = ["lib", "cli", "api", "service", "monorepo"]
            if profile not in valid_profiles:
                self.errors.append(
                    ValidationError(
                        f"Invalid profile '{profile}'. Must be one of: {', '.join(valid_profiles)}",
                        "project.profile",
                    )
                )

        # Python version validation
        python_version = project.get("python")
        if python_version:
            if not isinstance(python_version, str):
                self.errors.append(
                    ValidationError("Must be a string", "project.python")
                )
            elif not re.match(r"^\d+\.\d+$", python_version):
                self.errors.append(
                    ValidationError(
                        "Invalid Python version format. Use format like '3.11' or '3.12'",
                        "project.python",
                    )
                )

    def _validate_features_section(self, config: Config) -> None:
        """Validate the [features] section."""
        features = config.get("features", {})

        # Valid feature names
        valid_features = {
            "lint",
            "format",
            "test",
            "types",
            "pre_commit",
            "ci",
            "release",
            "docs",
            "security",
            "coverage",
        }

        for feature_name, feature_config in features.items():
            if feature_name not in valid_features:
                self.warnings.append(
                    ValidationWarning(
                        f"Unknown feature '{feature_name}'",
                        f"features.{feature_name}",
                        "Check documentation for supported features",
                    )
                )

            # Validate feature configuration
            if feature_name == "types":
                self._validate_types_feature(feature_config, feature_name)
            elif feature_name == "ci":
                self._validate_ci_feature(feature_config, feature_name)
            elif isinstance(feature_config, bool):
                # Boolean features are fine
                pass
            elif isinstance(feature_config, dict):
                # Dict features need validation based on feature type
                pass
            else:
                self.errors.append(
                    ValidationError(
                        f"Feature configuration must be boolean or dict, got {type(feature_config).__name__}",
                        f"features.{feature_name}",
                    )
                )

    def _validate_types_feature(self, config: Any, field_prefix: str) -> None:
        """Validate the types feature configuration."""
        if isinstance(config, str):
            valid_type_checkers = ["pyright", "mypy", "none"]
            if config not in valid_type_checkers:
                self.errors.append(
                    ValidationError(
                        f"Invalid type checker '{config}'. Must be one of: {', '.join(valid_type_checkers)}",
                        field_prefix,
                    )
                )
        elif isinstance(config, dict):
            enabled = config.get("enabled", False)
            if not isinstance(enabled, bool):
                self.errors.append(
                    ValidationError(
                        "enabled must be boolean", f"{field_prefix}.enabled"
                    )
                )

            checker = config.get("checker")
            if checker:
                valid_type_checkers = ["pyright", "mypy"]
                if checker not in valid_type_checkers:
                    self.errors.append(
                        ValidationError(
                            f"Invalid type checker '{checker}'. Must be one of: {', '.join(valid_type_checkers)}",
                            f"{field_prefix}.checker",
                        )
                    )
        elif isinstance(config, bool):
            # Boolean is fine
            pass
        else:
            self.errors.append(
                ValidationError(
                    "Types feature must be string, boolean, or dict", field_prefix
                )
            )

    def _validate_ci_feature(self, config: Any, field_prefix: str) -> None:
        """Validate the CI feature configuration."""
        if isinstance(config, str):
            valid_providers = ["github", "gitlab", "azure"]
            if config not in valid_providers:
                self.errors.append(
                    ValidationError(
                        f"Invalid CI provider '{config}'. Must be one of: {', '.join(valid_providers)}",
                        field_prefix,
                    )
                )
        elif isinstance(config, dict):
            provider = config.get("provider", "github")
            valid_providers = ["github", "gitlab", "azure"]
            if provider not in valid_providers:
                self.errors.append(
                    ValidationError(
                        f"Invalid CI provider '{provider}'. Must be one of: {', '.join(valid_providers)}",
                        f"{field_prefix}.provider",
                    )
                )

            python_versions = config.get("python")
            if python_versions:
                if isinstance(python_versions, list):
                    for version in python_versions:
                        if not isinstance(version, str) or not re.match(
                            r"^\d+\.\d+$", version
                        ):
                            self.errors.append(
                                ValidationError(
                                    f"Invalid Python version '{version}'. Use format like '3.11'",
                                    f"{field_prefix}.python",
                                )
                            )
                else:
                    self.errors.append(
                        ValidationError(
                            "python must be a list", f"{field_prefix}.python"
                        )
                    )
        elif isinstance(config, bool):
            # Boolean is fine
            pass
        else:
            self.errors.append(
                ValidationError(
                    "CI feature must be string, boolean, or dict", field_prefix
                )
            )

    def _validate_tooling_section(self, config: Config) -> None:
        """Validate the [tooling] section."""
        tooling = config.get("tooling", {})

        # Runner validation
        runner = tooling.get("runner")
        if runner:
            valid_runners = ["uv", "pip", "poetry", "pipenv"]
            if runner not in valid_runners:
                self.warnings.append(
                    ValidationWarning(
                        f"Unknown runner '{runner}'",
                        "tooling.runner",
                        f"Supported runners: {', '.join(valid_runners)}",
                    )
                )

        # Tasker validation
        tasker = tooling.get("tasker")
        if tasker:
            valid_taskers = ["just", "make", "task", "none"]
            if tasker not in valid_taskers:
                self.warnings.append(
                    ValidationWarning(
                        f"Unknown task runner '{tasker}'",
                        "tooling.tasker",
                        f"Supported task runners: {', '.join(valid_taskers)}",
                    )
                )

    def _validate_paths_section(self, config: Config) -> None:
        """Validate path-related sections."""
        # Validate format paths
        format_paths = config.get("format.paths", [])
        if format_paths:
            self._validate_path_list(format_paths, "format.paths")

        # Validate lint paths
        lint_paths = config.get("lint.paths", [])
        if lint_paths:
            self._validate_path_list(lint_paths, "lint.paths")

        # Validate test paths
        test_paths = config.get("test.paths", [])
        if test_paths:
            self._validate_path_list(test_paths, "test.paths")

    def _validate_path_list(self, paths: Any, field: str) -> None:
        """Validate a list of paths."""
        if not isinstance(paths, list):
            self.errors.append(ValidationError("Must be a list", field))
            return

        for path in paths:
            if not isinstance(path, str):
                self.errors.append(
                    ValidationError(
                        f"Path must be string, got {type(path).__name__}", field
                    )
                )
                continue

            # Check for common path issues
            if path.startswith("/"):
                self.warnings.append(
                    ValidationWarning(
                        f"Absolute path '{path}' may not be portable",
                        field,
                        "Use relative paths",
                    )
                )
            elif ".." in path:
                self.warnings.append(
                    ValidationWarning(
                        f"Path '{path}' contains '..' which may be unsafe",
                        field,
                        "Avoid parent directory references",
                    )
                )

    def _validate_ci_section(self, config: Config) -> None:
        """Validate the [ci] section."""
        ci = config.get("ci", {})

        # Python versions
        python_versions = ci.get("python")
        if python_versions:
            if isinstance(python_versions, list):
                for version in python_versions:
                    if not isinstance(version, str) or not re.match(
                        r"^\d+\.\d+$", version
                    ):
                        self.errors.append(
                            ValidationError(
                                f"Invalid Python version '{version}'. Use format like '3.11'",
                                "ci.python",
                            )
                        )
            else:
                self.errors.append(
                    ValidationError("python must be a list", "ci.python")
                )

        # Platforms
        platforms = ci.get("platforms")
        if platforms:
            if isinstance(platforms, list):
                valid_platforms = ["ubuntu-latest", "windows-latest", "macos-latest"]
                for platform in platforms:
                    if platform not in valid_platforms:
                        self.warnings.append(
                            ValidationWarning(
                                f"Unknown platform '{platform}'",
                                "ci.platforms",
                                f"Common platforms: {', '.join(valid_platforms)}",
                            )
                        )
            else:
                self.errors.append(
                    ValidationError("platforms must be a list", "ci.platforms")
                )

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        lines = []

        if self.errors:
            lines.append(f"❌ {len(self.errors)} error(s) found:")
            for error in self.errors:
                lines.append(f"  • {error}")

        if self.warnings:
            lines.append(f"⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                lines.append(f"  • {warning}")

        if not self.errors and not self.warnings:
            lines.append("✅ Configuration is valid")

        return "\n".join(lines)


def validate_config(config: Config) -> bool:
    """Validate configuration and return success status.

    Args:
        config: Configuration to validate

    Returns:
        True if valid, False otherwise
    """
    validator = ConfigValidator()
    return validator.validate(config)


def validate_config_with_report(config: Config) -> str:
    """Validate configuration and return detailed report.

    Args:
        config: Configuration to validate

    Returns:
        Validation report as string
    """
    validator = ConfigValidator()
    validator.validate(config)
    return validator.get_summary()
