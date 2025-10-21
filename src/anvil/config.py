"""Configuration management for Anvil."""

from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib
    from tomllib import TOMLKitError
except ImportError:
    import tomli as tomllib

    TOMLKitError = Exception  # Fallback for older tomli versions


class Config:
    """Anvil configuration manager."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize config manager.

        Args:
            project_root: Root directory of the project. Defaults to current working directory.
        """
        self.project_root = project_root or Path.cwd()
        self._config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from anvil.toml file.

        Returns:
            Configuration dictionary
        """
        config_file = self.project_root / "anvil.toml"
        if config_file.exists():
            try:
                with open(config_file, "rb") as f:
                    self._config = tomllib.load(f)
            except (TOMLKitError, OSError) as e:
                raise ValueError(f"Failed to load config from {config_file}: {e}")
        else:
            # Use default configuration
            self._config = self._get_default_config()

        return self._config

    def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to anvil.toml file.

        Args:
            config: Configuration to save. If None, saves current config.
        """
        if config is not None:
            self._config = config

        config_file = self.project_root / "anvil.toml"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # For now, we'll use a simple TOML writer
        # In a real implementation, we'd want to preserve comments and formatting
        with open(config_file, "w") as f:
            self._write_toml(f, self._config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Dot-separated key path (e.g., "project.name")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Dot-separated key path (e.g., "project.name")
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "project": {
                "name": "myproject",
                "package": "myproject",
                "python": "3.11",
                "profile": "lib",
            },
            "features": {
                "lint": True,
                "format": True,
                "test": True,
                "types": "pyright",
            },
            "tooling": {
                "runner": "uv",
                "tasker": "just",
            },
        }

    def _write_toml(self, file, data: Dict[str, Any], prefix: str = "") -> None:
        """Simple TOML writer (basic implementation).

        Args:
            file: File object to write to
            data: Data to write
            prefix: Current key prefix for nested structures
        """
        for key, value in data.items():
            if isinstance(value, dict):
                if prefix:
                    file.write(f"\n[{prefix}.{key}]\n")
                else:
                    file.write(f"\n[{key}]\n")
                self._write_toml(file, value, f"{prefix}.{key}" if prefix else key)
            else:
                if isinstance(value, str):
                    file.write(f'{key} = "{value}"\n')
                elif isinstance(value, bool):
                    file.write(f"{key} = {str(value).lower()}\n")
                else:
                    file.write(f"{key} = {value}\n")
