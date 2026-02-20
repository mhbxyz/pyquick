# Internal Alpha Release Checklist

[Project README](../../README.md) · [Docs Index](../README.md) · [Release and Feedback](README.md)

Use this checklist to run a repeatable, auditable go/no-go process for internal alpha.

## Release scope

- Target release: Internal Alpha
- Product scope: FastAPI profile (`new`, `dev`, `run`, `test`, `lint`, `fmt`, `check`)
- Packaging/runtime model: standalone PyQuick orchestration with delegated `uv` backend

## Go/No-Go Gates

Mark each gate as `pass`, `blocked`, or `waived` (with rationale).

| Gate | Command / Evidence | Expected | Owner | Status |
| --- | --- | --- | --- | --- |
| Functional workflow | `uv run pytest tests/e2e` | Full happy-path and failure-path E2E pass | QA Lead | pending |
| Core test suite | `uv run pytest` | Full suite green | QA Lead | pending |
| Quality tooling | `uv run pyqck check` | Deterministic check output, zero failures | Engineering | pending |
| Perf guardrails | `scripts/run_benchmarks.sh` | No regression beyond configured threshold | Performance Owner | pending |
| Docs readiness | Manual review of alpha docs links and command accuracy | Quickstart and troubleshooting are executable | DX/Docs Owner | pending |
| Release PR and env approvals | Release PR reviewed (if release-please path) + `testpypi`/`pypi` environment approvals recorded | Human go/no-go decisions are auditable | Release Manager | pending |
| GitHub release artifacts | Verify release notes + `.whl` and `.tar.gz` assets on tagged release | Release entry is complete and downloadable | Release Manager | pending |
| Release communication | Internal announcement draft + channel prepared | Audience, scope, known limits, feedback path included | Product/PM | pending |

## Ownership and Sign-off Matrix

| Area | Primary owner | Backup owner | Sign-off evidence | Signed |
| --- | --- | --- | --- | --- |
| Functional quality | QA Lead | Engineering | E2E + full suite output attached | no |
| Runtime/perf | Performance Owner | Engineering | benchmark report + compare output | no |
| Docs and onboarding | DX/Docs Owner | QA Lead | quickstart dry-run in clean environment | no |
| Release coordination | Product/PM | Engineering Lead | go/no-go note + announcement artifact | no |

Final go/no-go approver: Engineering Lead (with Product/PM acknowledgement).

## Release Rehearsal Runbook

Run in order on a clean local environment:

1. `uv sync --extra dev`
2. `uv run pytest`
3. `scripts/run_e2e.sh`
4. `scripts/run_benchmarks.sh`
5. `uv run pyqck --help` (command surface check)
6. Quickstart dry-run using [Alpha quickstart](../getting-started/quickstart-alpha.md)

Record rehearsal outcome:

- Date:
- Operator:
- Result: pass / blocked
- Notes:

## Packaging/Distribution and Announcement Steps

1. Confirm release commit hash and milestone closure state.
2. Confirm docs links resolve from `README.md`.
3. Confirm trusted publishing configuration from [PyPI trusted publishing](pypi-publishing.md).
4. Confirm release mode and review status from [Releasing PyQuick](releasing.md).
5. Confirm `testpypi` and `pypi` environment approvals are assigned.
6. Confirm GitHub release automation details from [GitHub release automation](github-releases.md).
7. Publish internal announcement including:
   - alpha scope
   - known constraints (including delegated `uv` backend)
   - how to onboard ([Alpha quickstart](../getting-started/quickstart-alpha.md))
   - where to report feedback ([issue template](../../.github/ISSUE_TEMPLATE/alpha-feedback.yml) and [Alpha feedback template](alpha-feedback-template.md))

## Feedback/Triage Loop (post-release)

1. Collect feedback through the alpha issue template.
2. Run triage using [Alpha triage process](triage-alpha-process.md).
3. Update ranked backlog in [Post-alpha roadmap](post-alpha-roadmap.md) after each cycle.

## Rollback and Contingency

Trigger rollback/hold if any of the following occurs during release rehearsal or immediately post-release:

- blocker in core workflow (`new -> run/dev -> test/check`)
- repeated E2E instability
- benchmark guardrail failure without approved waiver

Contingency actions:

1. Freeze announcement and mark release `on hold`.
2. Open blocker issue(s) with severity and owner.
3. Revert or patch forward on release branch/commit.
4. Re-run rehearsal steps after fix.
5. Re-announce only after all blocked gates are green.

Decision timebox for blocker triage: within 24 hours.

## See Also

- [Release and Feedback index](README.md)
- [Releasing PyQuick](releasing.md)
- [Alpha triage process](triage-alpha-process.md)
