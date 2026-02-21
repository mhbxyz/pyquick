# PyQuick v1 Command Contract

[Project README](../../README.md) · [Docs Index](../README.md) · [Reference](README.md)

Status: Accepted for milestone M1.

Note: profile/template evolution for M7 is specified in [Profile/template contract v2](profile-template-contract-v2.md). v1 command guarantees in this document remain normative for current shipped behavior.

This document defines the guaranteed behavior for v1 alpha commands and the shared execution conventions.

## Global Invariants

- Deterministic behavior: same inputs and environment must produce the same observable result.
- Idempotence: rerunning a command without changing inputs must not degrade project state.
- Actionable errors: failures must report what failed and how to recover.
- Stable command surface: command names in this document are v1 contract, not optional aliases.

## Exit Codes

- `0`: command completed successfully.
- `1`: runtime or managed-tool failure (subprocess execution, failing checks, watch failure).
- `2`: usage, input, or configuration error (invalid flags, invalid `pyquick.toml`, unsupported template/profile).

## Error Output Convention

- Prefix terminal failures with `ERROR` and a short category in brackets (`[config]`, `[tooling]`, `[usage]`).
- First line states the failure in one sentence.
- Follow with one recovery hint line beginning with `Hint:`.
- If caused by a subprocess, show executable name and propagated exit code.

Example:

```text
ERROR [tooling] Could not execute `ruff`.
Hint: Install dependencies with `pyqck install` and retry.
```

## Command Contract Matrix

| Command | Purpose | Inputs (v1) | Success Behavior | Failure Behavior | Idempotence Guarantee |
| --- | --- | --- | --- | --- | --- |
| `pyqck new <name> --profile api --template fastapi` | Scaffold a new API project | project name, profile, template | Creates scaffold with deterministic baseline files and returns `0` | Invalid profile/template or filesystem conflict returns `2`; generation failure returns `1` | Running again with same target path does not corrupt existing files and fails predictably unless overwrite is explicit |
| `pyqck install` (`pyqck sync` alias) | Sync project dependencies via packaging backend | optional passthrough flags (defaults to backend dev sync) | Executes backend sync and returns `0` on success | Invalid config returns `2`; backend/tooling failure returns propagated non-zero exit with actionable diagnostics | Re-running converges to the same environment/lock state for unchanged inputs |
| `pyqck dev` | Start dev feedback loop | optional config from `pyquick.toml` | Starts watcher/reload loop and exits `0` only on clean user stop | Invalid config returns `2`; watcher/tool process crash returns `1` | Re-running starts the same loop semantics with same config |
| `pyqck run` | Run app without dev watcher | optional run settings from config | Starts app process via configured defaults, exits with app code (success path `0`) | Invalid run config returns `2`; runner/tool errors return `1` | Re-running uses same launch contract and does not mutate config/project |
| `pyqck test` | Execute project test suite | optional passthrough flags | Runs configured test command and exits with propagated result | Invalid flags/config returns `2`; test runtime failure returns `1` | No persistent mutation outside normal test artifacts |
| `pyqck lint` | Run lint checks | optional passthrough flags | Runs lint checks and reports concise status | Invalid flags/config returns `2`; lint execution/failing lint returns `1` | Repeatable and read-only on source |
| `pyqck fmt` | Apply formatting | optional passthrough flags | Applies deterministic formatting and returns `0` on success | Invalid flags/config returns `2`; formatter failure returns `1` | Running repeatedly converges with no additional changes after first clean run |
| `pyqck check` | Run full quality gate pipeline | optional scope flags (if defined), config defaults | Runs lint, type-check, tests in deterministic order and returns `0` when all pass | Invalid config/flags returns `2`; any check failure returns `1` with per-step summary | Same input set yields same step ordering and result summary |

## Non-Goals for v1 Alpha

The following are explicitly out of scope for v1 and must not be introduced during M1-M3 unless this document is revised:

- Plugin API ecosystem.
- Flask/Litestar parity.
- Database scaffolding by default.
- Advanced CI generation.

See decision record: [ADR 0001](../adr/0001-defer-v1-non-goals.md).

## Implementation Mapping (M1)

This section makes #1 directly testable against follow-up issues.

- `#2` config schema and validation:
  - Implement exit code `2` for invalid config and unknown-key policy.
  - Ensure defaults match command matrix assumptions for `dev`, `run`, `check`.
- `#3` tool adapters:
  - Standardize subprocess error reporting with `[tooling]` category and hint.
  - Propagate subprocess exit behavior into command result (`1` on tool failure).
  - Resolve tools through semantic config keys: `packaging`, `linting`, `testing`, `typing`, `running`.
  - Execute Python tooling via `packaging run <tool>` (default: `uv run <tool>`).
- `#4` command wrappers:
  - Match command names and purpose exactly.
  - Emit consistent final status lines and deterministic pipeline order for `check`.

## Review Checklist

- Each v1 command has explicit success/failure semantics and exit codes.
- Non-goals are documented and link to an ADR.
- Error messaging format is consistent and actionable.
- The contract can be consumed in one page by maintainers.

## See Also

- [Reference index](README.md)
- [Config example](examples/pyquick.toml)
