# Profile/Template Contract v2

[Project README](../../README.md) · [Docs Index](../README.md) · [Reference](README.md)

Status: Accepted for milestone M7.

This document defines the stable contract for selecting `profile` and `template` in `pyqck new` beyond the current API-first alpha baseline.

## Goals

- Provide a stable profile/template contract that can evolve without command-surface breakage.
- Make validation behavior explicit and testable.
- Define migration boundaries from v1 (`api` + `fastapi`) assumptions.

## Non-Goals (v2)

- Shipping all reserved profiles immediately.
- Guaranteeing framework parity across all future profile families.
- Defining a plugin API for third-party templates.

## Profile Taxonomy

Two profile groups are defined:

- **Supported now**: available in current shipped scaffold behavior.
- **Reserved**: part of contract vocabulary but not yet scaffold-capable.

| Profile | Contract status | Implementation status | Notes |
| --- | --- | --- | --- |
| `api` | stable | supported | current alpha baseline |
| `lib` | stable | supported | baseline library scaffold |
| `cli` | stable keyword | reserved | planned follow-up (#26) |
| `web` | stable keyword | reserved | taxonomy placeholder |
| `game` | stable keyword | reserved | taxonomy placeholder |

Reserved means the identifier is recognized by product vocabulary, but attempts to scaffold it may return a usage error until a compatible template is implemented.

## Template Naming and Compatibility

Template names are lowercase kebab-case strings.

Compatibility is defined by profile/template pair, not by template alone.

| Profile | Default template | Compatible templates now | Planned compatible templates |
| --- | --- | --- | --- |
| `api` | `fastapi` | `fastapi` | additional API templates may be added later |
| `lib` | `baseline-lib` | `baseline-lib` | additional library templates may be added later |
| `cli` | `baseline-cli` | none (reserved) | `baseline-cli` |
| `web` | n/a | none (reserved) | tbd |
| `game` | n/a | none (reserved) | tbd |

### Compatibility Rules

1. `profile` must be one of the contract taxonomy values.
2. `template` must exist in the catalog for that profile.
3. If `template` is omitted, use the profile default template.
4. Unknown profile, unknown template, reserved-not-yet-supported profile, and incompatible profile/template pair are usage failures.

## Defaults and Validation Order

`pyqck new <name>` defaults to:

- `profile=api`
- `template=fastapi`

Validation order is normative:

1. Validate `profile` taxonomy membership.
2. Validate profile implementation availability.
3. Resolve default `template` for selected profile when omitted.
4. Validate template membership and compatibility for the profile.

## Exit Codes and Error Conventions

Validation failures return exit code `2` and follow the usage convention:

- First line: `ERROR [usage] <message>`
- Second line: `Hint: <recovery guidance>`

Representative examples:

```text
ERROR [usage] Unsupported profile.
Hint: Use one of: api, lib, cli, web, game.
```

```text
ERROR [usage] Profile `lib` is reserved and not scaffoldable yet.
Hint: Use `--profile api --template fastapi` until lib templates ship.
```

```text
ERROR [usage] Unsupported template.
Hint: Use a template compatible with selected profile.
```

```text
ERROR [usage] Template `fastapi` is not compatible with profile `cli`.
Hint: Choose a template from the profile template catalog.
```

## Migration Note From v1 API-First Assumptions

What stays stable:

- `pyqck new <name> --profile api --template fastapi` remains valid.
- Exit code and error-category conventions stay unchanged.

What becomes explicit in v2:

- Profile taxonomy is defined independently from immediate implementation.
- Template compatibility is profile-scoped and contract-driven.

What is not implied:

- Reserved profiles (`lib`, `cli`, `web`, `game`) are not guaranteed scaffoldable until their follow-up issues land.

## Follow-Up Implementation Mapping

- #25: introduce profile/template registry abstraction and command routing.
- #24: implement `lib` profile baseline template.
- #26: implement `cli` profile baseline template.

## Contract Test Matrix

| Case | Input | Expected result |
| --- | --- | --- |
| valid api pair | `pyqck new demo --profile api --template fastapi` | success (`0`) |
| default pair | `pyqck new demo` | resolved to `api/fastapi`, success (`0`) |
| unknown profile | `pyqck new demo --profile worker` | usage failure (`2`) |
| reserved profile today | `pyqck new demo --profile lib` | usage failure (`2`) with reserved hint |
| unknown template | `pyqck new demo --template flask` | usage failure (`2`) |
| incompatible pair | `pyqck new demo --profile cli --template fastapi` | usage failure (`2`) |

## See Also

- [Command contract v1](command-contract-v1.md)
- [Issue #31](https://github.com/mhbxyz/pyquick/issues/31)
- [Issue #25](https://github.com/mhbxyz/pyquick/issues/25)
- [Issue #24](https://github.com/mhbxyz/pyquick/issues/24)
- [Issue #26](https://github.com/mhbxyz/pyquick/issues/26)
