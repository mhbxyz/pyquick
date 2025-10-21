# Technologies and Technical Details

## Core Technologies

### Programming Language
- **Python 3.11+**: Primary implementation language
- **Type Hints**: Full type annotation support throughout codebase
- **Async/Await**: Used for I/O operations and long-running tasks

### Build System and Packaging
- **uv**: Fast Python package installer and resolver
- **pyproject.toml**: Modern Python packaging standard
- **pipx**: For isolated CLI tool installation

### Code Quality Tools
- **Ruff**: Fast Python linter and formatter (replaces flake8, isort, black)
- **pytest**: Testing framework with rich plugin ecosystem
- **mypy/pyright**: Type checking (configurable preference)
- **bandit**: Security linting (optional)
- **pip-audit**: Dependency vulnerability scanning (optional)

### Development Tools
- **watchdog**: File system monitoring for dev mode
- **rich**: Beautiful terminal output and progress bars
- **click**: Command-line interface framework
- **tomli/tomllib**: TOML parsing (tomllib in Python 3.11+)

## Development Setup

### Local Development
- **Python 3.11+** required
- **uv** for dependency management
- **pre-commit** hooks for code quality
- **VS Code** with Python extensions recommended

### Project Structure
```
anvil/
├── src/anvil/          # Main package
│   ├── cli.py         # CLI entry point
│   ├── config.py      # Configuration parsing
│   ├── profiles/      # Built-in profiles
│   ├── features/      # Built-in features
│   └── plugins.py     # Plugin system
├── tests/             # Test suite
├── docs/              # Documentation
└── pyproject.toml     # Package configuration
```

### Testing Strategy
- **Unit Tests**: Core functionality with pytest
- **Integration Tests**: End-to-end command testing
- **Plugin Tests**: Plugin loading and compatibility
- **Cross-Platform Tests**: macOS, Linux, Windows CI

## Technical Constraints

### Performance Requirements
- **CLI Startup**: <100ms cold start
- **Command Execution**: <1s for typical operations on small projects
- **Memory Usage**: Minimal footprint for CLI tool

### Compatibility
- **Python Versions**: 3.11+ (following modern Python ecosystem)
- **Operating Systems**: macOS, Linux, Windows
- **Terminal Support**: Standard terminals with ANSI color support

### Plugin System Constraints
- **Entry Points**: Standard Python entry point mechanism
- **Version Compatibility**: Semantic versioning for plugin API
- **Isolation**: Plugins run in separate process/context when needed

## Dependencies

### Core Dependencies
- `click >= 8.0`: CLI framework
- `rich >= 13.0`: Terminal UI
- `tomli >= 2.0; python_version < "3.11"`: TOML parsing
- `watchdog >= 3.0`: File monitoring
- `pyyaml >= 6.0`: YAML support for advanced configs

### Optional Dependencies
- `uv >= 0.1`: Fast package management
- `ruff >= 0.1`: Code quality
- `pytest >= 7.0`: Testing
- `mypy >= 1.0` or `pyright >= 1.1`: Type checking
- `bandit >= 1.7`: Security scanning
- `pip-audit >= 2.0`: Vulnerability checking

## Tool Usage Patterns

### Configuration Management
- Single `anvil.toml` file per project
- TOML format for human readability
- Version-controllable configuration
- Profile-based defaults with overrides

### Error Handling
- Clear, actionable error messages
- Non-zero exit codes for CI/CD
- Graceful degradation when tools unavailable
- Structured logging with appropriate verbosity levels

### Plugin Architecture
- Entry point discovery for automatic loading
- Version compatibility checking
- Clean API boundaries between core and plugins
- Documentation and examples for plugin development