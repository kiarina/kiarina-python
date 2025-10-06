---
title: Procedure for adding a new package to the UV workspace
description: >-
  The correct procedure for adding a namespace package to a uv workspace.
  Editable installation is performed automatically.
---

## Key points

- `uv pip install -e` is not required (workspace automatically performs editable installation)
- Configuration in `[tool.uv.sources]` is mandatory
- `uv sync` properly sets up the entire workspace

## Procedure

### 1. Create package directory
```sh
mkdir packages/new-package-name
cd packages/new-package-name
uv init
```

### 2. Update root pyproject.toml

#### Add to workspace members
```toml
[tool.uv.workspace]
members = [
    "packages/existing-package",
    "packages/new-package-name",  # Add this
]
```

#### Add to dependencies
```toml
[project]
dependencies = [
    "existing-package",
    "new-package-name",  # Add this
]
```

#### Add to workspace sources
```toml
[tool.uv.sources]
existing-package = { workspace = true }
new-package-name = { workspace = true }  # Add this
```

#### Add to mypy_path
```toml
[mypy]
mypy_path = [
    "packages/existing-package",
    "packages/new-package-name",  # Add this
]
```

#### Add to coverage.run source
```toml
[tool.coverage.run]
source = [
    "packages/existing-package/src",
    "packages/new-package-name/src",  # Add this
]
```

### 3. Add to meta package (if applicable)
If you have a meta package that aggregates multiple packages, add the new package to its dependencies.
```toml
[project]
dependencies = [
    "existing-package>=1.0.0",
    "new-package-name>=1.1.0",  # Add this
]
```

### 4. Sync the environment
```sh
uv sync --all-packages --all-extras --all-groups
```
