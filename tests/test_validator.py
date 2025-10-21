"""Tests for configuration validation."""

import tempfile
from pathlib import Path

from anvil.config import Config
from anvil.validator import (
    ConfigValidator,
    ValidationError,
    ValidationWarning,
    validate_config,
    validate_config_with_report,
)


class TestConfigValidator:
    """Test configuration validation functionality."""

    def test_valid_config(self):
        """Test validation of a valid configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"
python = "3.11"

[features]
lint = true
format = true
test = true
types = "pyright"
pre_commit = true
ci = "github"

[tooling]
runner = "uv"
tasker = "just"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert validator.validate(config)
            assert len(validator.errors) == 0
            assert len(validator.warnings) == 0

    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[features]
lint = true
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 3  # name, package, profile
            assert any("name" in str(error) for error in validator.errors)
            assert any("package" in str(error) for error in validator.errors)
            assert any("profile" in str(error) for error in validator.errors)

    def test_invalid_project_name(self):
        """Test validation of invalid project names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "123invalid"
package = "test_project"
profile = "lib"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 1
            assert "project.name" in str(validator.errors[0])

    def test_invalid_package_name(self):
        """Test validation of invalid package names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "123invalid"
profile = "lib"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 1
            assert "project.package" in str(validator.errors[0])

    def test_invalid_profile(self):
        """Test validation of invalid profile."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "invalid"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 1
            assert "project.profile" in str(validator.errors[0])

    def test_invalid_python_version(self):
        """Test validation of invalid Python version."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"
python = "3.11.0"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 1
            assert "project.python" in str(validator.errors[0])

    def test_unknown_feature_warning(self):
        """Test warning for unknown features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"

[features]
unknown_feature = true
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert validator.validate(config)
            assert len(validator.errors) == 0
            assert len(validator.warnings) == 1
            assert "unknown_feature" in str(validator.warnings[0])

    def test_invalid_types_feature(self):
        """Test validation of invalid types feature configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"

[features]
types = "invalid_checker"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 1
            assert "types:" in str(validator.errors[0])

    def test_valid_types_feature_dict(self):
        """Test validation of valid types feature dict configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"

[features.types]
enabled = true
checker = "pyright"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert validator.validate(config)
            assert len(validator.errors) == 0

    def test_invalid_ci_python_versions(self):
        """Test validation of invalid CI Python versions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"

[ci]
python = ["3.11", "invalid.version"]
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert not validator.validate(config)
            assert len(validator.errors) == 1
            assert "ci.python" in str(validator.errors[0])

    def test_unknown_tooling_warning(self):
        """Test warning for unknown tooling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"

[tooling]
runner = "unknown_runner"
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert validator.validate(config)
            assert len(validator.errors) == 0
            assert len(validator.warnings) == 1
            assert "tooling.runner" in str(validator.warnings[0])

    def test_absolute_path_warning(self):
        """Test warning for absolute paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"

[format]
paths = ["/absolute/path"]
""")

            config = Config(Path(temp_dir))
            validator = ConfigValidator()

            assert validator.validate(config)
            assert len(validator.errors) == 0
            assert len(validator.warnings) == 1
            assert "absolute path" in str(validator.warnings[0]).lower()

    def test_validation_summary(self):
        """Test validation summary generation."""
        validator = ConfigValidator()
        validator.errors.append(ValidationError("Test error", "test.field"))
        validator.warnings.append(ValidationWarning("Test warning", "test.field"))

        summary = validator.get_summary()
        assert "1 error(s) found" in summary
        assert "1 warning(s)" in summary
        assert "Test error" in summary
        assert "Test warning" in summary

    def test_validation_summary_valid(self):
        """Test validation summary for valid config."""
        validator = ConfigValidator()
        # No errors or warnings

        summary = validator.get_summary()
        assert "Configuration is valid" in summary


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_config_function(self):
        """Test the validate_config function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"
""")

            config = Config(Path(temp_dir))
            assert validate_config(config)

    def test_validate_config_with_report_function(self):
        """Test the validate_config_with_report function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "anvil.toml"
            config_file.write_text("""
[project]
name = "test-project"
package = "test_project"
profile = "lib"
""")

            config = Config(Path(temp_dir))
            report = validate_config_with_report(config)
            assert "Configuration is valid" in report
