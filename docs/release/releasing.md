# Releasing PyQuick

[Project README](../../README.md) · [Docs Index](../README.md) · [Release and Feedback](README.md)

This guide defines the two supported release paths and the mandatory human go/no-go points.

## Which workflow should I use?

- **Manual release (`release-manual.yml`)**: fastest path for immediate alpha/hotfix release needs.
- **Release-please (`release-please.yml`)**: default path for ongoing semver/changelog automation with human review.

In both paths, publishing to TestPyPI/PyPI remains gated by protected environments and approvals.

## Prerequisites

- You can dispatch workflows from `main`.
- Trusted publishing environments are configured (`testpypi`, `pypi`).
- Release approvers are assigned for environment approvals.
- Commit messages follow conventional commit style.

## Commit conventions for version bumps

- `feat:` -> minor bump
- `fix:` -> patch bump
- `feat!:` or `refactor!:` ->
  - on `0.x` (alpha): **minor bump**
  - on `1.x+`: major bump

This behavior is configured via release-please (`bump-minor-pre-major: true`).

## Path A: Manual release (Phase 1)

Workflow: `.github/workflows/release-manual.yml`

### Inputs

- `bump`: `patch|minor|major`
- `preflight`: run `uv sync --extra dev`, `uv run pytest`, and `scripts/run_benchmarks.sh`

### Execution flow

1. Dispatch from `main`.
2. Workflow validates branch and checks latest CI status on `main`.
3. Optional preflight runs.
4. Version is bumped in `pyproject.toml`.
5. Commit is created: `chore(release): vX.Y.Z`.
6. Tag `vX.Y.Z` is created and pushed.
7. Existing `publish.yml` runs from tag push and handles TestPyPI -> verify -> PyPI -> GitHub Release.

### Guardrails

- Fails if dispatched outside `main`.
- Fails if preflight is enabled and any check fails.
- Fails if target tag already exists.
- `publish.yml` fails on version/tag mismatch.

## Path B: Release-please (Phase 2)

Workflow: `.github/workflows/release-please.yml`

### Execution flow

1. On updates to `main`, release-please opens/updates a release PR.
2. Release PR contains version bump + changelog draft.
3. Human review + merge is required (go/no-go point).
4. release-please creates the release tag on merge.
5. Existing `publish.yml` runs from the tag and performs publishing gates.

### Human control points

- Release PR must be reviewed and merged manually.
- `testpypi` and `pypi` environment approvals remain manual.
- No silent publishing occurs without explicit approvals.

## Dry-run examples

### Minor alpha release (`v0.3.0`)

1. Dispatch `release-manual.yml` with `bump=minor`, `preflight=true`.
2. Confirm commit `chore(release): v0.3.0` appears on `main`.
3. Confirm tag `v0.3.0` exists and triggers `publish.yml`.
4. Approve `testpypi`, then `pypi` when ready.
5. Verify GitHub Release has wheel/sdist artifacts.

### Patch hotfix (`v0.3.1`)

1. Merge fix PR to `main`.
2. Either:
   - dispatch manual release with `bump=patch`, or
   - merge the release-please PR that proposes patch bump.
3. Validate publish pipeline and release artifacts.

## Incident runbook

### If failure happens after TestPyPI publish

1. Stop before approving `pypi` environment.
2. Open/label blocker issue with failing job logs.
3. Apply fix on `main` and rerun release from a new version.

### If tag exists but publish fails

1. Do not reuse or rewrite the same tag.
2. Fix root cause on `main`.
3. Cut a new patch release (`vX.Y.(Z+1)`).

### Yank version / re-release

1. If a bad build reached PyPI, yank the bad version on PyPI.
2. Prepare a patch release with the fix.
3. Publish the new version and document migration guidance in release notes.

## Validation checklist (Done criteria)

- A contributor can run release end-to-end from docs only.
- Version/tag/changelog are produced by workflow, not ad hoc local steps.
- Manual controls remain on release PR review and publishing environment approvals.

## See Also

- [PyPI trusted publishing](pypi-publishing.md)
- [GitHub release automation](github-releases.md)
- [Alpha release checklist](release-alpha-checklist.md)
