# Release

[English](README.md) | [日本語](README.ja.md)

Procedure for releasing kiarina-python to PyPI.

This guide explains the release procedure using version 2.2.0 as an example.

## v2.2.0 Release Procedure

### 1. Update Version

Before updating versions, add release details to the `Unreleased` section of:

- Root `CHANGELOG.md`: Summary of changes for all packages
- `packages/kiarina/CHANGELOG.md`: Same summary for the `kiarina` meta-package
- `packages/<package-name>/CHANGELOG.md`: Detailed changes for each changed package

```sh
# Update the root, kiarina, and packages with unreleased changes
mise run pyproject:bump-version 2.2.0
```

The root project and `kiarina` meta-package are always updated. Other packages
are updated only when their `Unreleased` section contains changes. The
meta-package dependency lower bounds are also updated for those packages.

### 2. Update CHANGELOG

Replace `Unreleased` with the release version in the root and packages whose
version matches `2.2.0`:

```sh
mise run changelog:bump-version 2.2.0
```

Packages whose version does not match the release version are left unchanged.
The task fails if a selected package has no changelog content.

### 3. Review Changes
```sh
# Review changed files
git diff
```

### 4. Run CI Checks
```sh
# Ensure all CI checks pass
mise run ci
```

### 5. Commit, Tag, and Push
```sh
# Commit changes
git add .
git commit -m "chore: bump version to 2.2.0"

# Create annotated tag
git tag -s v2.2.0 -m "Release v2.2.0"

# Push with tags
git push --tags
```

## Automated Processes

When you push a tag, the `.github/workflows/release.yml` workflow in GitHub Actions automatically executes the following processes:

1. **CI Checks**: Runs lint, test, and build
2. **GitHub Release**: Automatically creates a GitHub Release with release notes
3. **Release Build**: Builds only packages whose version matches the tag
4. **PyPI Publication**: Publishes all release packages in a single operation (if `PYPI_API_TOKEN` is configured)
