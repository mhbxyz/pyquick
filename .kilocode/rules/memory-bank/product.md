# Product Description

## Why Anvil Exists

Anvil was created to solve the repetitive and error-prone process of setting up Python projects. Developers often spend significant time configuring build tools, linters, formatters, testing frameworks, and CI/CD pipelines for each new project. This leads to inconsistent setups, forgotten configurations, and wasted time that could be spent on actual development.

The Python ecosystem has excellent tools (uv, ruff, black, pytest, etc.), but integrating them consistently across projects requires manual effort. Anvil standardizes this process, providing a unified CLI that scaffolds projects with best practices built-in.

## Problems It Solves

1. **Repetitive Setup**: Eliminates the need to manually create Makefiles, configure pre-commit hooks, set up CI/CD, and manage dependencies for every project.

2. **Inconsistent Tooling**: Ensures all projects use the same versions of tools and follow the same conventions, reducing cognitive load and maintenance overhead.

3. **Onboarding Friction**: New team members can quickly understand and contribute to projects without spending days learning custom build setups.

4. **Plugin Ecosystem Complexity**: Provides a clean plugin system for extending functionality without conflicting with core features.

5. **Cross-Platform Development**: Works seamlessly on macOS, Linux, and Windows with consistent behavior.

## How It Works

Anvil is a CLI tool that reads configuration from `anvil.toml` files to understand project requirements. It provides commands like `new`, `dev`, `run`, `fmt`, `lint`, `test`, `build`, and `release` that work consistently across all projects.

### Core Workflow
1. **Scaffold**: Use `anvil new` with profiles (lib, cli, api, service, monorepo) to create project structure and initial configuration.
2. **Develop**: Use `anvil dev` for watch mode development with automatic linting and testing.
3. **Maintain**: Use `anvil fmt`, `anvil lint`, `anvil test` for code quality and testing.
4. **Release**: Use `anvil build` and `anvil release` for packaging and publishing.

### Key Features
- **Profiles**: Opinionated blueprints for different project types
- **Plugins**: Extensible system for adding new features and profiles
- **Idempotent Commands**: Safe to run multiple times without side effects
- **Fallback Gracefully**: Works even when preferred tools aren't available
- **Single Source of Truth**: `anvil.toml` drives all configuration

## User Experience Goals

1. **Zero-Config Start**: New projects should work immediately after `anvil new` without additional setup.

2. **Fast Feedback**: Commands like `anvil dev` and `anvil check` provide quick feedback during development.

3. **Consistent Experience**: All projects feel familiar regardless of their type or complexity.

4. **Extensible**: Easy to add new features via plugins without modifying core code.

5. **Reliable**: Commands are deterministic and fail fast with clear error messages.

6. **Discoverable**: `anvil --help` and command suggestions guide users to the right tools.

7. **Cross-Platform**: Works identically on all major operating systems.

8. **Performance**: Core operations complete in under 1 second for small projects.