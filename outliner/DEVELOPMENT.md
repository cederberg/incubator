# Development

## Release Checklist

- Run `cd outliner && make outdated` and verify zero updates
- Update `outliner/pyproject.toml` version
- Update `outliner/CHANGELOG.md`
- Run `cd outliner && make clean test`
- Commit the version and changelog updates
- Tag the release as `outliner-vX.Y.Z`
- Push the commit and tag
- Wait for GitHub Actions `publish-outliner` workflow to complete
- Verify release on PyPI and GitHub
