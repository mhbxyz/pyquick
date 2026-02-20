# GitHub Release Automation

[Project README](../../README.md) · [Docs Index](../README.md) · [Release and Feedback](README.md)

PyQuick creates GitHub Releases from version tags and attaches package artifacts.

## Trigger

Release automation runs when a tag matching `v*` is pushed.

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Workflow behavior

Workflow: `.github/workflows/publish.yml`

1. Validates tag/version consistency (`vX.Y.Z` must match `pyproject.toml` version).
2. Builds package artifacts (`.whl`, `.tar.gz`).
3. Publishes to TestPyPI.
4. Verifies installation from TestPyPI.
5. Publishes to PyPI.
6. Creates GitHub Release with generated notes and attached artifacts.

## Generated release contents

- Auto-generated GitHub release notes.
- Uploaded artifacts:
  - `dist/*.whl`
  - `dist/*.tar.gz`
- Standard migration note block (CLI/config/repo naming).

## Failure modes

- Tag/version mismatch -> workflow fails in build job.
- Missing artifacts -> release job fails before publishing release.
- Trusted publishing failure -> release is not created.

## See Also

- [PyPI trusted publishing](pypi-publishing.md)
- [Alpha release checklist](release-alpha-checklist.md)
