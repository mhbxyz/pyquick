# System Architecture

## Overview
Anvil is a Python CLI tool that orchestrates development toolchains for Python projects. It follows a plugin-based architecture with a configuration-driven approach, using TOML files as the single source of truth for project settings.

## Core Components

### 1. CLI Framework
- **Entry Point**: `anvil` command with subcommands
- **Command Structure**: Hierarchical commands (new, dev, run, fmt, lint, etc.)
- **Idempotent Operations**: All commands can be run multiple times safely

### 2. Configuration System
- **Primary Config**: `anvil.toml` - project-specific configuration
- **Fallback Config**: Global user configuration (optional)
- **TOML Format**: Human-readable, version-controllable configuration

### 3. Profile System
- **Built-in Profiles**: lib, cli, api, service, monorepo
- **Profile Templates**: Define project structure, dependencies, and defaults
- **Extensible**: Plugin system allows custom profiles

### 4. Plugin Architecture
- **Entry Points**: Python entry points for features and profiles
- **Plugin Discovery**: Automatic detection and loading
- **Compatibility**: Version constraints via metadata

### 5. Command Execution Engine
- **Tool Detection**: Automatic detection of available tools (uv, ruff, black, etc.)
- **Fallback Behavior**: Graceful degradation when preferred tools unavailable
- **Cross-Platform**: Consistent behavior across macOS, Linux, Windows

## Key Design Decisions

### Configuration-Driven
- All behavior determined by `anvil.toml` configuration
- No hardcoded assumptions about project structure
- Single source of truth for project settings

### Plugin-Based Extensibility
- Core functionality minimal and focused
- Plugins add features without modifying core
- Clean separation between core and extensions

### Idempotent Operations
- Commands can be run repeatedly without side effects
- Safe to re-run failed operations
- Predictable behavior

### Tool Agnostic with Preferences
- Supports multiple tools for same functionality (e.g., black vs. ruff for formatting)
- Configurable tool preferences
- Automatic fallback to available tools

## Component Relationships

```
CLI Commands
    ↓
Configuration Parser (anvil.toml)
    ↓
Profile Loader
    ↓
Plugin System
    ↓
Tool Executors
    ↓
File System Operations
```

## Critical Implementation Paths

### Project Scaffolding (`anvil new`)
1. Parse command arguments (profile, template, name)
2. Load profile configuration
3. Generate project structure
4. Create `anvil.toml` with defaults
5. Initialize basic files (pyproject.toml, src/, tests/)

### Development Mode (`anvil dev`)
1. Read `anvil.toml` for watch paths and commands
2. Set up file watchers
3. On change: run lint + test commands
4. Display results with clear feedback

### Command Execution
1. Parse `anvil.toml` for tool preferences
2. Check tool availability
3. Execute with appropriate runner
4. Handle errors and fallbacks gracefully

## Data Flow

### Configuration Flow
```
anvil.toml → Config Parser → Profile Merger → Effective Config → Command Execution
```

### Plugin Loading Flow
```
Entry Points → Plugin Discovery → Compatibility Check → Feature Registration → Command Enhancement
```

## Error Handling
- **Fail Fast**: Clear error messages for configuration issues
- **Graceful Degradation**: Continue with available tools when preferred ones missing
- **Non-Zero Exits**: Commands fail appropriately for CI/CD integration