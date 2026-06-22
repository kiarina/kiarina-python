# Add New Package

[English](README.md) | [日本語](README.ja.md)

uv workspace に namespace package を追加するための手順です。

## Key points

- `uv pip install -e` は不要です（workspace が自動的に editable installation を行います）
- `[tool.uv.sources]` の設定は必須です
- `uv sync` によって workspace 全体が正しくセットアップされます

## Procedure

### 1. Create package directory

以下は次の条件の例です。

- パッケージ名は `new-package-name`
- namespace は `kiarina.lib.hoge`

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

`packages/new-package-name/src/kiarina/lib/hoge/__init__.py` を作成し、次の内容を記述します。

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

`src/kiarina` や `src/kiarina/lib` の下には `__init__.py` を作成しないでください。

#### Add a sample module

サンプルモジュール `packages/new-package-name/src/kiarina/lib/hoge/_hello.py` を作成します。

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

テストファイル `packages/new-package-name/tests/test_hello.py` を作成します。

```python
from kiarina.lib.hoge import hello

def test_hello():
    assert hello() == "Hello, world!"
```

#### Add pytest configuration to VSCode

```sh
mkdir packages/new-package-name/.vscode
```

`packages/new-package-name/.vscode/settings.json` に次の内容を追加します。

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

複数パッケージを集約するメタパッケージがある場合は、新しいパッケージをその dependencies に追加します。

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
