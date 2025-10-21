"""Patch engine for applying anvil.toml configuration to project files."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional
from datetime import datetime


class PatchType(Enum):
    """Types of patches that can be applied."""

    CREATE_FILE = "create_file"
    UPDATE_FILE = "update_file"
    DELETE_FILE = "delete_file"
    ADD_DEPENDENCY = "add_dependency"
    UPDATE_DEPENDENCY = "update_dependency"
    REMOVE_DEPENDENCY = "remove_dependency"


class FileFormat(Enum):
    """Supported file formats for patching."""

    TOML = "toml"
    YAML = "yaml"
    JSON = "json"
    PYTHON = "python"
    TEXT = "text"


@dataclass
class PatchOperation:
    """Represents a single patch operation."""

    patch_type: PatchType
    target_path: Path
    description: str
    data: Optional[Any] = None
    backup_data: Optional[Any] = None
    file_format: Optional[FileFormat] = None


@dataclass
class PatchResult:
    """Result of applying a patch operation."""

    operation: PatchOperation
    success: bool
    message: str
    applied_at: Optional[datetime] = None

    def __post_init__(self):
        if self.success and not self.applied_at:
            self.applied_at = datetime.now()


class Patch(ABC):
    """Abstract base class for patches."""

    def __init__(self, description: str):
        self.description = description
        self.operations: List[PatchOperation] = []

    @abstractmethod
    def generate_operations(
        self, config: "Config", project_root: Path
    ) -> List[PatchOperation]:
        """Generate the operations needed to apply this patch.

        Args:
            config: Project configuration
            project_root: Root directory of the project

        Returns:
            List of patch operations to apply
        """
        pass

    def apply(
        self, config: "Config", project_root: Path, dry_run: bool = False
    ) -> List[PatchResult]:
        """Apply this patch to the project.

        Args:
            config: Project configuration
            project_root: Root directory of the project
            dry_run: If True, only simulate the changes

        Returns:
            List of patch results
        """
        if not self.operations:
            self.operations = self.generate_operations(config, project_root)

        results = []
        for operation in self.operations:
            result = self._apply_operation(operation, project_root, dry_run)
            results.append(result)

        return results

    def _apply_operation(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Apply a single patch operation.

        Args:
            operation: The operation to apply
            project_root: Root directory of the project
            dry_run: If True, only simulate the changes

        Returns:
            Result of the operation
        """
        try:
            if operation.patch_type == PatchType.CREATE_FILE:
                return self._create_file(operation, project_root, dry_run)
            elif operation.patch_type == PatchType.UPDATE_FILE:
                return self._update_file(operation, project_root, dry_run)
            elif operation.patch_type == PatchType.DELETE_FILE:
                return self._delete_file(operation, project_root, dry_run)
            elif operation.patch_type in (
                PatchType.ADD_DEPENDENCY,
                PatchType.UPDATE_DEPENDENCY,
                PatchType.REMOVE_DEPENDENCY,
            ):
                return self._modify_dependency(operation, project_root, dry_run)
            else:
                return PatchResult(
                    operation=operation,
                    success=False,
                    message=f"Unsupported patch type: {operation.patch_type}",
                )
        except Exception as e:
            return PatchResult(
                operation=operation,
                success=False,
                message=f"Failed to apply operation: {e}",
            )

    def _create_file(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Create a new file."""
        target_path = project_root / operation.target_path

        if target_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"File already exists: {target_path}",
            )

        if not dry_run:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if operation.file_format == FileFormat.TEXT:
                target_path.write_text(operation.data or "")
            else:
                # For structured formats, data should be the parsed content
                self._write_structured_file(
                    target_path, operation.data, operation.file_format
                )

        return PatchResult(
            operation=operation, success=True, message=f"Created file: {target_path}"
        )

    def _update_file(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Update an existing file."""
        target_path = project_root / operation.target_path

        if not target_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"File does not exist: {target_path}",
            )

        if not dry_run:
            # Backup current content
            operation.backup_data = target_path.read_text()

            if operation.file_format == FileFormat.TEXT:
                target_path.write_text(operation.data or "")
            else:
                # For structured formats, merge the data
                current_data = self._read_structured_file(
                    target_path, operation.file_format
                )
                merged_data = self._merge_data(current_data, operation.data)
                self._write_structured_file(
                    target_path, merged_data, operation.file_format
                )

        return PatchResult(
            operation=operation, success=True, message=f"Updated file: {target_path}"
        )

    def _delete_file(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Delete a file."""
        target_path = project_root / operation.target_path

        if not target_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"File does not exist: {target_path}",
            )

        if not dry_run:
            # Backup current content
            operation.backup_data = target_path.read_text()
            target_path.unlink()

        return PatchResult(
            operation=operation, success=True, message=f"Deleted file: {target_path}"
        )

    def _modify_dependency(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Modify a dependency in pyproject.toml."""
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"pyproject.toml not found: {pyproject_path}",
            )

        # This would need to parse and modify pyproject.toml
        # For now, return a placeholder
        return PatchResult(
            operation=operation,
            success=False,
            message="Dependency modification not yet implemented",
        )

    def _read_structured_file(self, file_path: Path, file_format: FileFormat) -> Any:
        """Read and parse a structured file."""
        content = file_path.read_text()

        if file_format == FileFormat.TOML:
            try:
                import tomllib

                return tomllib.loads(content)
            except ImportError:
                import tomli as tomllib

                return tomllib.loads(content)
        elif file_format == FileFormat.JSON:
            import json

            return json.loads(content)
        elif file_format == FileFormat.YAML:
            import yaml

            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _write_structured_file(
        self, file_path: Path, data: Any, file_format: FileFormat
    ) -> None:
        """Write data to a structured file."""
        if file_format == FileFormat.TOML:
            # For TOML, we'd need a TOML writer that preserves comments
            # This is a simplified version
            try:
                import tomli_w

                tomli_w.dump(data, file_path.open("wb"))
            except ImportError:
                # Fallback to basic TOML writing
                self._write_basic_toml(file_path, data)
        elif file_format == FileFormat.JSON:
            import json

            file_path.write_text(json.dumps(data, indent=2))
        elif file_format == FileFormat.YAML:
            import yaml

            yaml.dump(data, file_path, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _write_basic_toml(self, file_path: Path, data: Any) -> None:
        """Basic TOML writer fallback."""
        content = ""
        for key, value in data.items():
            if isinstance(value, dict):
                content += f"\n[{key}]\n"
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        content += f'{sub_key} = "{sub_value}"\n'
                    elif isinstance(sub_value, bool):
                        content += f"{sub_key} = {str(sub_value).lower()}\n"
                    elif isinstance(sub_value, list):
                        content += f"{sub_key} = {sub_value}\n"
                    else:
                        content += f"{sub_key} = {sub_value}\n"
            else:
                if isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                elif isinstance(value, bool):
                    content += f"{key} = {str(value).lower()}\n"
                elif isinstance(value, list):
                    content += f"{key} = {value}\n"
                else:
                    content += f"{key} = {value}\n"
        file_path.write_text(content)

    def _merge_data(self, current: Any, updates: Any) -> Any:
        """Merge update data into current data."""
        if isinstance(current, dict) and isinstance(updates, dict):
            merged = current.copy()
            for key, value in updates.items():
                if (
                    key in merged
                    and isinstance(merged[key], dict)
                    and isinstance(value, dict)
                ):
                    merged[key] = self._merge_data(merged[key], value)
                else:
                    merged[key] = value
            return merged
        else:
            # For non-dict types, updates replace current
            return updates


class FeaturePatch(Patch):
    """Patch for enabling/disabling features."""

    def __init__(self, feature_name: str, enabled: bool):
        description = f"{'Enable' if enabled else 'Disable'} {feature_name} feature"
        super().__init__(description)
        self.feature_name = feature_name
        self.enabled = enabled

    def generate_operations(
        self, config: "Config", project_root: Path
    ) -> List[PatchOperation]:
        """Generate operations to enable/disable a feature."""
        operations = []

        # Example: Add pre-commit hooks if pre_commit feature is enabled
        if self.feature_name == "pre_commit" and self.enabled:
            operations.extend(self._generate_pre_commit_operations(project_root))

        # Example: Add CI configuration if ci feature is enabled
        elif self.feature_name == "ci" and self.enabled:
            operations.extend(self._generate_ci_operations(config, project_root))

        return operations

    def _generate_pre_commit_operations(
        self, project_root: Path
    ) -> List[PatchOperation]:
        """Generate operations for pre-commit setup."""
        operations = []

        # Create .pre-commit-config.yaml
        pre_commit_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.4.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-added-large-files"},
                    ],
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "23.7.0",
                    "hooks": [{"id": "black"}],
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "5.12.0",
                    "hooks": [{"id": "isort"}],
                },
            ]
        }

        operations.append(
            PatchOperation(
                patch_type=PatchType.CREATE_FILE,
                target_path=Path(".pre-commit-config.yaml"),
                description="Create pre-commit configuration",
                data=pre_commit_config,
                file_format=FileFormat.YAML,
            )
        )

        return operations

    def _generate_ci_operations(
        self, config: "Config", project_root: Path
    ) -> List[PatchOperation]:
        """Generate operations for CI setup."""
        operations = []

        ci_provider = config.get("ci.provider", "github")
        if ci_provider == "github":
            # Create GitHub Actions workflow
            workflow_content = {
                "name": "CI",
                "on": ["push", "pull_request"],
                "jobs": {
                    "test": {
                        "runs-on": "ubuntu-latest",
                        "strategy": {
                            "matrix": {
                                "python-version": config.get(
                                    "ci.python", ["3.11", "3.12"]
                                )
                            }
                        },
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {
                                "name": "Set up Python ${{ matrix.python-version }}",
                                "uses": "actions/setup-python@v4",
                                "with": {
                                    "python-version": "${{ matrix.python-version }}"
                                },
                            },
                            {
                                "name": "Install dependencies",
                                "run": "pip install uv && uv sync",
                            },
                            {"name": "Run tests", "run": "uv run pytest"},
                        ],
                    }
                },
            }

            operations.append(
                PatchOperation(
                    patch_type=PatchType.CREATE_FILE,
                    target_path=Path(".github/workflows/ci.yml"),
                    description="Create GitHub Actions CI workflow",
                    data=workflow_content,
                    file_format=FileFormat.YAML,
                )
            )

        return operations


class PatchEngine:
    """Engine for applying patches to projects."""

    def __init__(self):
        self.applied_patches: List[PatchResult] = []

    def _read_structured_file(self, file_path: Path, file_format: FileFormat) -> Any:
        """Read and parse a structured file."""
        content = file_path.read_text()

        if file_format == FileFormat.TOML:
            try:
                import tomllib

                return tomllib.loads(content)
            except ImportError:
                import tomli as tomllib

                return tomllib.loads(content)
        elif file_format == FileFormat.JSON:
            import json

            return json.loads(content)
        elif file_format == FileFormat.YAML:
            import yaml

            return yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _write_structured_file(
        self, file_path: Path, data: Any, file_format: FileFormat
    ) -> None:
        """Write data to a structured file."""
        if file_format == FileFormat.TOML:
            # For TOML, we'd need a TOML writer that preserves comments
            # This is a simplified version
            try:
                import tomli_w

                tomli_w.dump(data, file_path.open("wb"))
            except ImportError:
                # Fallback to basic TOML writing
                self._write_basic_toml(file_path, data)
        elif file_format == FileFormat.JSON:
            import json

            file_path.write_text(json.dumps(data, indent=2))
        elif file_format == FileFormat.YAML:
            import yaml

            with open(file_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def _write_basic_toml(self, file_path: Path, data: Any) -> None:
        """Basic TOML writer fallback."""
        content = ""
        for key, value in data.items():
            if isinstance(value, dict):
                content += f"\n[{key}]\n"
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        content += f'{sub_key} = "{sub_value}"\n'
                    elif isinstance(sub_value, bool):
                        content += f"{sub_key} = {str(sub_value).lower()}\n"
                    elif isinstance(sub_value, list):
                        content += f"{sub_key} = {sub_value}\n"
                    else:
                        content += f"{sub_key} = {sub_value}\n"
            else:
                if isinstance(value, str):
                    content += f'{key} = "{value}"\n'
                elif isinstance(value, bool):
                    content += f"{key} = {str(value).lower()}\n"
                elif isinstance(value, list):
                    content += f"{key} = {value}\n"
                else:
                    content += f"{key} = {value}\n"
        file_path.write_text(content)

    def _merge_data(self, current: Any, updates: Any) -> Any:
        """Merge update data into current data."""
        if isinstance(current, dict) and isinstance(updates, dict):
            merged = current.copy()
            for key, value in updates.items():
                if (
                    key in merged
                    and isinstance(merged[key], dict)
                    and isinstance(value, dict)
                ):
                    merged[key] = self._merge_data(merged[key], value)
                else:
                    merged[key] = value
            return merged
        else:
            # For non-dict types, updates replace current
            return updates

    def plan_changes(
        self, config: "Config", project_root: Path
    ) -> List[PatchOperation]:
        """Plan all changes that would be applied based on configuration.

        Args:
            config: Project configuration
            project_root: Root directory of the project

        Returns:
            List of all operations that would be performed
        """
        operations = []

        # Generate patches based on enabled features
        features = config.get("features", {})

        for feature_name, feature_config in features.items():
            if isinstance(feature_config, bool) and feature_config:
                patch = FeaturePatch(feature_name, True)
                operations.extend(patch.generate_operations(config, project_root))
            elif isinstance(feature_config, dict) and feature_config.get(
                "enabled", False
            ):
                patch = FeaturePatch(feature_name, True)
                operations.extend(patch.generate_operations(config, project_root))

        # Filter out operations for files that already exist
        filtered_operations = []
        for operation in operations:
            target_path = project_root / operation.target_path
            if operation.patch_type == PatchType.CREATE_FILE and target_path.exists():
                continue  # Skip creating files that already exist
            filtered_operations.append(operation)

        return filtered_operations

    def apply_changes(
        self,
        config: "Config",
        project_root: Path,
        force: bool = False,
        dry_run: bool = False,
    ) -> List[PatchResult]:
        """Apply all changes based on configuration.

        Args:
            config: Project configuration
            project_root: Root directory of the project
            force: If True, apply changes without confirmation
            dry_run: If True, only simulate changes

        Returns:
            List of patch results
        """
        operations = self.plan_changes(config, project_root)

        if not operations:
            return []

        if not dry_run and not force:
            # In a real implementation, we'd prompt for confirmation
            # For now, we'll just proceed
            pass

        results = []
        for operation in operations:
            # Apply operation directly without creating abstract patch instance
            result = self._apply_single_operation(operation, project_root, dry_run)
            results.append(result)
            if result.success and not dry_run:
                self.applied_patches.append(result)

        return results

    def _apply_single_operation(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Apply a single patch operation directly."""
        try:
            if operation.patch_type == PatchType.CREATE_FILE:
                return self._create_file_operation(operation, project_root, dry_run)
            elif operation.patch_type == PatchType.UPDATE_FILE:
                return self._update_file_operation(operation, project_root, dry_run)
            elif operation.patch_type == PatchType.DELETE_FILE:
                return self._delete_file_operation(operation, project_root, dry_run)
            elif operation.patch_type in (
                PatchType.ADD_DEPENDENCY,
                PatchType.UPDATE_DEPENDENCY,
                PatchType.REMOVE_DEPENDENCY,
            ):
                return self._modify_dependency_operation(
                    operation, project_root, dry_run
                )
            else:
                return PatchResult(
                    operation=operation,
                    success=False,
                    message=f"Unsupported patch type: {operation.patch_type}",
                )
        except Exception as e:
            return PatchResult(
                operation=operation,
                success=False,
                message=f"Failed to apply operation: {e}",
            )

    def _create_file_operation(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Create a new file."""
        target_path = project_root / operation.target_path

        if target_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"File already exists: {target_path}",
            )

        if not dry_run:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if operation.file_format == FileFormat.TEXT:
                target_path.write_text(operation.data or "")
            else:
                # For structured formats, data should be the parsed content
                self._write_structured_file(
                    target_path, operation.data, operation.file_format
                )

        return PatchResult(
            operation=operation, success=True, message=f"Created file: {target_path}"
        )

    def _update_file_operation(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Update an existing file."""
        target_path = project_root / operation.target_path

        if not target_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"File does not exist: {target_path}",
            )

        if not dry_run:
            # Backup current content
            operation.backup_data = target_path.read_text()

            if operation.file_format == FileFormat.TEXT:
                target_path.write_text(operation.data or "")
            else:
                # For structured formats, merge the data
                current_data = self._read_structured_file(
                    target_path, operation.file_format
                )
                merged_data = self._merge_data(current_data, operation.data)
                self._write_structured_file(
                    target_path, merged_data, operation.file_format
                )

        return PatchResult(
            operation=operation, success=True, message=f"Updated file: {target_path}"
        )

    def _delete_file_operation(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Delete a file."""
        target_path = project_root / operation.target_path

        if not target_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"File does not exist: {target_path}",
            )

        if not dry_run:
            # Backup current content
            operation.backup_data = target_path.read_text()
            target_path.unlink()

        return PatchResult(
            operation=operation, success=True, message=f"Deleted file: {target_path}"
        )

    def _modify_dependency_operation(
        self, operation: PatchOperation, project_root: Path, dry_run: bool
    ) -> PatchResult:
        """Modify a dependency in pyproject.toml."""
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            return PatchResult(
                operation=operation,
                success=False,
                message=f"pyproject.toml not found: {pyproject_path}",
            )

        # This would need to parse and modify pyproject.toml
        # For now, return a placeholder
        return PatchResult(
            operation=operation,
            success=False,
            message="Dependency modification not yet implemented",
        )

    def rollback(self, project_root: Path) -> List[PatchResult]:
        """Rollback all applied patches.

        Args:
            project_root: Root directory of the project

        Returns:
            List of rollback results
        """
        results = []

        for patch_result in reversed(self.applied_patches):
            operation = patch_result.operation

            if operation.backup_data is not None:
                # Restore from backup
                target_path = project_root / operation.target_path

                if operation.patch_type == PatchType.UPDATE_FILE:
                    target_path.write_text(operation.backup_data)
                    results.append(
                        PatchResult(
                            operation=operation,
                            success=True,
                            message=f"Restored file: {target_path}",
                        )
                    )
                elif operation.patch_type == PatchType.DELETE_FILE:
                    target_path.write_text(operation.backup_data)
                    results.append(
                        PatchResult(
                            operation=operation,
                            success=True,
                            message=f"Restored deleted file: {target_path}",
                        )
                    )

        # Clear applied patches after rollback
        self.applied_patches.clear()

        return results
