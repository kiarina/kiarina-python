# Add New Package

English | [日本語](README.ja.md)

Procedure for adding a namespace package to the uv workspace.

## Key points

- `uv pip install -e` is not required. The workspace performs editable installation.
- In the root `pyproject.toml`, update `[tool.uv.workspace]`, `[tool.uv.sources]`, `[tool.mypy]`, and `[tool.coverage.run]`.
- The root `pyproject.toml` has no `[project].dependencies`. Add new distribution packages to the meta package in `packages/kiarina/pyproject.toml` when applicable.
- Create `README.ja.md` first, then create `README.md` as a complete mirror after the content is stable.
- Dependencies used only under `{mod}_impl.{name}` must be optional dependencies.

## Procedure

Here is an example where:

- the package name is `new-package-name`
- the public namespace is `kiarina.lib.hoge`

### 1. Create package directory

```sh
mkdir packages/new-package-name
cd packages/new-package-name
uv init
```

Configure `pyproject.toml` by following existing packages.

- `[project]` fields: `name`, `version`, `description`, `readme`, `license`, `authors`, `maintainers`, `keywords`, `classifiers`, `requires-python`, and `dependencies`
- `[project.optional-dependencies]` when optional dependencies are available
- `[project.urls]` entries: `Homepage`, `Repository`, `Issues`, `Changelog`, and `Documentation`
- `[build-system]`
- `[tool.hatch.build.targets.wheel]`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/kiarina"]
```

### 2. Add package files

Create at least these files.

```text
packages/new-package-name/
  CHANGELOG.md
  Makefile
  README.ja.md
  README.md
  pyproject.toml
  .mise/tasks/package/current
  .vscode/settings.json
  tests/.pytest-args
  tests/__init__.py
  tests/conftest.py
```

If environment variables are needed only for VS Code, also create `.env.vscode`. Do not put secrets themselves in this file.

```text
packages/new-package-name/.env.vscode
```

Create `CHANGELOG.md` with an `Unreleased` section. Do not add change entries until just before committing.

### 3. Add namespace package

Do not place `__init__.py` at namespace package boundaries.

```sh
mkdir -p packages/new-package-name/src/kiarina/lib/hoge
touch packages/new-package-name/src/kiarina/lib/hoge/py.typed
```

Do not create `__init__.py` files under `src/kiarina` or under `src/kiarina/lib`.

Split features into feature subpackages according to Crystal Architecture instead of implementing functionality directly under the top-level module.

```text
src/kiarina/lib/hoge/
  feature/
    __init__.py
    _helpers/
    _models/
    _schemas/
    _services/
    _instances/
    _types/
    _views/
```

Create only the directories that are needed. Collect public APIs in each subpackage's `__init__.py`.

When using lazy imports, keep source-group comments in both `__all__` and `module_map`.

```python
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_hoge import create_hoge
    from ._models.hoge import Hoge

__all__ = [
    # ._helpers
    "create_hoge",
    # ._models
    "Hoge",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_hoge": "._helpers.create_hoge",
        # ._models
        "Hoge": "._models.hoge",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
```

### 4. Add tests

Mirror the `src` structure in tests.

```text
src/kiarina/lib/hoge/feature/_helpers/create_hoge.py
tests/feature/_helpers/test_create_hoge.py
```

Write default pytest arguments in `tests/.pytest-args`.

```text
--timeout 120
-rs
-v
```

Add parallel execution and reruns when the package needs them, following existing packages.

```text
-n 8
--timeout 30
--reruns 3
--reruns-delay 5
-rs
-v
```

### 5. Add VS Code settings

Create `packages/new-package-name/.vscode/settings.json`.

```json
{
    "python.testing.pytestArgs": [
        "tests",
        "-rs",
        "-v"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.envFile": "${workspaceFolder}/.env.vscode"
}
```

If package-local env is not needed, omit `python.envFile` and `.env.vscode`.

Add the package to the `folders` list in the root `vscode.code-workspace`.

```json
{
  "path": "packages/new-package-name"
}
```

### 6. Add Makefile and mise task

The package `Makefile` should delegate to root tasks.

```makefile
.PHONY: format lint test build clean check
.DEFAULT_GOAL := check

format:
	mise run format
lint:
	mise run lint
test:
	mise run test
build:
	mise run build
clean:
	mise run clean
check:
	mise run format
	mise run lint
	mise run test --coverage
```

If the package has costly tests or provider-specific tests, add explicit shortcut targets.

```makefile
.PHONY: provider_openai_test
provider_openai_test:
	mise run test --costly --path tests/provider_impl/openai
```

Create `packages/new-package-name/.mise/tasks/package/current`.

```bash
#!/usr/bin/env bash
#MISE description="Print the current package name"

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
basename "$(dirname "$(dirname "$(dirname "$script_dir")")")"
```

### 7. Update root pyproject.toml

Add the package to `[tool.uv.workspace].members`.

```toml
[tool.uv.workspace]
members = [
    "packages/existing-package",
    "packages/new-package-name",
]
```

Add the package to `[tool.uv.sources]`.

```toml
[tool.uv.sources]
existing-package = { workspace = true }
new-package-name = { workspace = true }
```

Add `src` to `[tool.mypy].mypy_path`.

```toml
[tool.mypy]
mypy_path = [
    "packages/existing-package/src",
    "packages/new-package-name/src",
]
```

Add `src` to `[tool.coverage.run].source`.

```toml
[tool.coverage.run]
source = [
    "packages/existing-package/src",
    "packages/new-package-name/src",
]
```

### 8. Add optional dependencies

Dependencies used only under `{mod}_impl.{name}` must be optional dependencies.

Name the extra `{mod}-{name}` and replace `_` with `-`.

```toml
[project.optional-dependencies]
all = [
    "google-cloud-storage>=3.4.0",
]
asset-repository-gcs = [
    "google-cloud-storage>=3.4.0",
]
```

Wrap dependency imports in `try-except`. On `ImportError`, identify the class or feature that requires the dependency and suggest the extra installation command.

```python
try:
    from google.cloud.storage import Client
except ImportError as exc:
    raise ImportError(
        "google-cloud-storage is required to use GCSAssetRepository. "
        "Install it with: "
        "pip install 'new-package-name[asset-repository-gcs]'"
    ) from exc
```

See [Implementation Optional Dependencies](../../concepts/implementation_optional_dependencies/README.md) for details.

### 9. Update repository surfaces

Add the package to the `Packages` table in the root `README.ja.md` and `README.md`. Keep both README files as complete mirrors in different languages.

Add regular distribution packages to the meta package dependencies in `packages/kiarina/pyproject.toml`. If the package should not be included in the meta package, make that reason explicit.

Follow [Package README Structure](../../playbooks/package_readme_structure/README.md) for package README files.

### 10. Sync and verify

Sync the environment.

```sh
uv sync --all-packages --all-extras --all-groups
```

Confirm the package appears in the package list.

```sh
mise run package:list
```

Verify the target package.

```sh
mise run lint new-package-name
mise run test new-package-name
mise run build new-package-name
```

If code changed, also run `make` at the repository root.

```sh
make
```
