# Add New Package

[English](README.md) | 日本語

uv workspace に namespace package を追加するための手順です。

## Key points

- `uv pip install -e` は不要です。workspace が editable installation を行います。
- root `pyproject.toml` では `[tool.uv.workspace]`、`[tool.uv.sources]`、`[tool.mypy]`、`[tool.coverage.run]` を更新します。
- root `pyproject.toml` に `[project].dependencies` はありません。新しい配布パッケージは、必要に応じて `packages/kiarina/pyproject.toml` の meta package に追加します。
- package README は `README.ja.md` を先に作り、内容が固まったら `README.md` を完全なミラーとして作ります。
- `{mod}_impl.{name}` 以下だけで使う依存は optional dependency にします。

## Procedure

以下は次の条件の例です。

- package name は `new-package-name`
- public namespace は `kiarina.lib.hoge`

### 1. Create package directory

```sh
mkdir packages/new-package-name
cd packages/new-package-name
uv init
```

`pyproject.toml` は、既存 package を参考にして次の情報を設定します。

- `[project]` の `name`、`version`、`description`、`readme`、`license`、`authors`、`maintainers`、`keywords`、`classifiers`、`requires-python`、`dependencies`
- optional dependency がある場合は `[project.optional-dependencies]`
- `[project.urls]` の `Homepage`、`Repository`、`Issues`、`Changelog`、`Documentation`
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

最低限、次のファイルを作成します。

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

VS Code だけで使う環境変数が必要な場合は、`.env.vscode` も作成します。secret そのものは置かないでください。

```text
packages/new-package-name/.env.vscode
```

`CHANGELOG.md` は `Unreleased` セクションを持つ形式で作成します。ただし、commit 直前までは変更内容を追記しません。

### 3. Add namespace package

namespace package の境界には `__init__.py` を置きません。

```sh
mkdir -p packages/new-package-name/src/kiarina/lib/hoge
touch packages/new-package-name/src/kiarina/lib/hoge/py.typed
```

`src/kiarina` や `src/kiarina/lib` の下には `__init__.py` を作成しないでください。

機能は top-level module 直下ではなく、Crystal Architecture に沿って feature subpackage に分けます。

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

必要な directory だけを作成します。公開 API は各 subpackage の `__init__.py` に集約します。

lazy import を使う場合は、`__all__` と `module_map` に import 元ごとのグループコメントを残します。

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

test は `src` の構造を mirror します。

```text
src/kiarina/lib/hoge/feature/_helpers/create_hoge.py
tests/feature/_helpers/test_create_hoge.py
```

pytest の既定引数は `tests/.pytest-args` に書きます。

```text
--timeout 120
-rs
-v
```

並列実行や rerun が必要な package では、既存 package と同じように追加します。

```text
-n 8
--timeout 30
--reruns 3
--reruns-delay 5
-rs
-v
```

### 5. Add VS Code settings

`packages/new-package-name/.vscode/settings.json` を作成します。

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

package-local env が不要な場合は `python.envFile` と `.env.vscode` を省略できます。

root `vscode.code-workspace` の `folders` に package を追加します。

```json
{
  "path": "packages/new-package-name"
}
```

### 6. Add Makefile and mise task

package `Makefile` は root task に委譲します。

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

costly test や provider 別 test がある場合は、明示的な shortcut target を追加します。

```makefile
.PHONY: provider_openai_test
provider_openai_test:
	mise run test --costly --path tests/provider_impl/openai
```

`packages/new-package-name/.mise/tasks/package/current` を作成します。

```bash
#!/usr/bin/env bash
#MISE description="Print the current package name"

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
basename "$(dirname "$(dirname "$(dirname "$script_dir")")")"
```

### 7. Update root pyproject.toml

`[tool.uv.workspace].members` に追加します。

```toml
[tool.uv.workspace]
members = [
    "packages/existing-package",
    "packages/new-package-name",
]
```

`[tool.uv.sources]` に追加します。

```toml
[tool.uv.sources]
existing-package = { workspace = true }
new-package-name = { workspace = true }
```

`[tool.mypy].mypy_path` に `src` を追加します。

```toml
[tool.mypy]
mypy_path = [
    "packages/existing-package/src",
    "packages/new-package-name/src",
]
```

`[tool.coverage.run].source` に `src` を追加します。

```toml
[tool.coverage.run]
source = [
    "packages/existing-package/src",
    "packages/new-package-name/src",
]
```

### 8. Add optional dependencies

`{mod}_impl.{name}` 以下だけで使う依存 package は optional dependency にします。

extra 名は `{mod}-{name}` とし、`_` は `-` に置き換えます。

```toml
[project.optional-dependencies]
all = [
    "google-cloud-storage>=3.4.0",
]
asset-repository-gcs = [
    "google-cloud-storage>=3.4.0",
]
```

依存 package の import は `try-except` で囲みます。`ImportError` では、利用する class または機能と extra の install command を案内します。

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

詳しくは [Implementation Optional Dependencies](../../concepts/implementation_optional_dependencies/README.ja.md) を参照してください。

### 9. Update repository surfaces

root `README.ja.md` と `README.md` の `Packages` 表に package を追加します。両方の README は言語違いの完全なミラーとして維持します。

通常の配布対象 package は、`packages/kiarina/pyproject.toml` の meta package dependencies にも追加します。meta package に含めない場合は、その理由を明確にします。

package README は [Package README Structure](../../playbooks/package_readme_structure/README.ja.md) に従います。

### 10. Sync and verify

環境を同期します。

```sh
uv sync --all-packages --all-extras --all-groups
```

package list に表示されることを確認します。

```sh
mise run package:list
```

対象 package を確認します。

```sh
mise run lint new-package-name
mise run test new-package-name
mise run build new-package-name
```

コードを変更した場合は root で `make` も実行します。

```sh
make
```
