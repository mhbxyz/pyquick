# PyPI Trusted Publishing

[Project README](../../README.md) · [Docs Index](../README.md) · [Release and Feedback](README.md)

This guide documents how `pyqck` is published to TestPyPI and PyPI via GitHub OIDC trusted publishing.

## Workflows

- Build validation: `.github/workflows/python-package.yml`
  - runs on PR and `main`
  - builds wheel/sdist via `uv build`
  - smoke-installs built wheel and runs `pyqck --help`
- Publish pipeline: `.github/workflows/publish.yml`
  - runs on version tags (`v*`)
  - publishes to TestPyPI
  - verifies install from TestPyPI
  - publishes to PyPI
  - creates GitHub Release with wheel/sdist assets

## One-time setup on TestPyPI and PyPI

Configure **Trusted Publisher** on both indexes with:

- Owner: `mhbxyz`
- Repository: `pyquick`
- Workflow: `publish.yml`
- Environment: `testpypi` (for TestPyPI) and `pypi` (for PyPI)

No API token is required once trusted publishing is configured.

## Release trigger

Publish flow is tag-driven:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Expected sequence:

1. build artifacts
2. publish TestPyPI
3. install smoke from TestPyPI
4. publish PyPI
5. create GitHub Release

## Troubleshooting

- If TestPyPI install verification fails intermittently, rerun once after index propagation.
- If publish fails with OIDC/trust errors, confirm trusted publisher binding exactly matches owner/repo/workflow.
- If version already exists, bump version and create a new tag.

## See Also

- [Release and Feedback index](README.md)
- [Alpha release checklist](release-alpha-checklist.md)
- [GitHub release automation](github-releases.md)
