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
Here is an example where:
- the package name is `new-package-name`
- the namespace is `kiarina.lib.hoge`

#### Create package directory and initialize with `uv init`
```sh
mkdir packages/new-package-name
cd packages/new-package-name
uv init
```

#### Add `py.typed` file
```sh
mkdir -p packages/new-package-name/src/kiarina/lib/hoge
touch packages/new-package-name/src/kiarina/lib/hoge/py.typed
```

#### Add `__init__.py` file
Create `packages/new-package-name/src/kiarina/lib/hoge/__init__.py` with the following content:
```python
# __init__.py
import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._hello import hello

__version__ = version("new-package-name")

__all__ = ["hello"]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "hello": "._hello",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
```
Do not create `__init__.py` files under `src/kiarina` or under `src/kiarina/lib`.

#### Add a sample module
Create a sample module `packages/new-package-name/src/kiarina/lib/hoge/_hello.py`.
```python
def hello() -> str:
    return "Hello, world!"
```

#### Add tests
```sh
mkdir -p packages/new-package-name/tests
touch packages/new-package-name/tests/__init__.py
touch packages/new-package-name/tests/conftest.py
```
Create a test file `packages/new-package-name/tests/test_hello.py`.
```python
from kiarina.lib.hoge import hello

def test_hello():
    assert hello() == "Hello, world!"
```

#### Add pytest configuration to VSCode
```sh
mkdir packages/new-package-name/.vscode
```

Add the following to `packages/new-package-name/.vscode/settings.json`.
```json
{
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
}
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
