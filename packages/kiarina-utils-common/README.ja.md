# kiarina-utils-common

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-utils-common.svg)](https://badge.fury.io/py/kiarina-utils-common)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-common.svg)](https://pypi.org/project/kiarina-utils-common/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

kiarina namespace 内で、最も汎用的なユーティリティを提供するパッケージ。

## Installation

```bash
pip install kiarina-utils-common
```

## API Reference

### `import_object`

```python
import_object(import_path)
```

`module_name:object_name` 形式の import path から object を import して返します。

**Parameters**

- `import_path` (`str`): `module_name:object_name` 形式の import path
  - 例: `kiarina.utils.common:parse_config_string`

**Returns**

- import された class、function、またはその他の object

**Raises**

- `ValueError`: import path の形式が不正な場合
- `ImportError`: module を import できない場合
- `AttributeError`: module 内に object が存在しない場合

**Examples**

```python
# function を import
parse_fn = import_object("kiarina.utils.common:parse_config_string")
result = parse_fn("key=value")

# class を import
MyClass = import_object("myapp.plugins:MyPlugin")
instance = MyClass()

# type hint を指定
from typing import Callable

parser: Callable = import_object("kiarina.utils.common:parse_config_string")
```

### `parse_config_string`

```python
parse_config_string(
    config_str,
    *,
    separator="&",
    key_value_separator="=",
    nested_separator=".",
    brackets="()",
)
```

設定文字列を `dict[str, Any]` に parse します。`brackets` で囲まれた値は区切り文字を含めても 1 つの値として扱われ、型変換も抑制されます。

**Parameters**

- `config_str` (`str`): parse する設定文字列
- `separator` (`str`): item の区切り文字。default: `"&"`
- `key_value_separator` (`str`): key と value の区切り文字。default: `"="`
- `nested_separator` (`str`): nested key の区切り文字。default: `"."`
- `brackets` (`str`): 区切り文字を含む value を囲む 2 文字の組。default: `"()"`。無効にする場合は `""`

**Returns**

- `dict[str, Any]`: parse された設定 dictionary

**Examples**

```python
# 基本的な使用方法
parse_config_string("key1=value1&key2=value2")
# {"key1": "value1", "key2": "value2"}

# nested key
parse_config_string("cache.enabled=true&db.port=5432")
# {"cache": {"enabled": True}, "db": {"port": 5432}}

# value のない flag
parse_config_string("debug&verbose")
# {"debug": None, "verbose": None}

# brackets で囲まれた value
parse_config_string("k=(a&b=c)&n=5")
# {"k": "a&b=c", "n": 5}

# custom separator
parse_config_string("a:1;b:2", separator=";", key_value_separator=":")
# {"a": 1, "b": 2}
```

### `ConfigRegistry`

名前、alias、default を使って設定を管理し、設定文字列や keyword argument で値を上書きして解決します。取得した設定は deep copy されるため、登録元の設定は変更されません。

```python
from kiarina.utils.config_registry import ConfigRegistry

registry = ConfigRegistry[dict[str, object]](
    get_default=lambda: "standard",
    get_aliases=lambda: {"default": "standard"},
    get_presets=lambda: {
        "standard": {"model": "example", "temperature": 0.5},
    },
)

config = registry.get("default?temperature=0.8")
# {"model": "example", "temperature": 0.8}

resolved = registry.resolve("standard")
print(resolved.name)
print(resolved.config)
```

**Key methods**

- `register(name, config)` / `unregister(name)`: runtime の設定を登録・解除
- `get(specifier=None, **kwargs)`: 解決した設定を取得
- `resolve(specifier=None, **kwargs)`: 解決後の名前と設定を `ResolvedConfig` として取得
- `list_names()` / `list_aliases()`: 利用可能な名前と alias を取得
- `clear()`: runtime に登録した設定を削除

### `ComponentRegistry`

class や factory を名前で管理し、必要なときに新しい instance を生成します。import path で定義された preset や custom component も利用できます。

```python
from kiarina.utils.component_registry import ComponentRegistry


class Client:
    def __init__(self, endpoint: str = "") -> None:
        self.endpoint = endpoint


registry = ComponentRegistry(expected_type=Client)
registry.register("client", Client)

client = registry.resolve("client?endpoint=https://example.com")
```

**Key methods**

- `register(name, factory)` / `unregister(name)`: component factory を登録・解除
- `create(name, *args, **kwargs)`: 名前を指定して新しい instance を生成
- `resolve(input=None, *args, **kwargs)`: instance または specifier を解決
- `get(name)`: runtime に登録された factory を取得
- `list_names()` / `list_aliases()`: 利用可能な名前と alias を取得
- `clear()`: runtime に登録した factory を削除

### `ObjectRegistry`

`ConfigRegistry` で設定を解決し、その設定から object を生成します。`get()` は生成した object を保持して再利用し、`create()` と `resolve()` は毎回新しい object を生成します。

```python
from kiarina.utils.object_registry import ObjectRegistry


class Client:
    def __init__(self, endpoint: str = "") -> None:
        self.endpoint = endpoint


registry = ObjectRegistry[Client, dict[str, object]](
    expected_type=Client,
    get_default=lambda: "default",
    get_presets=lambda: {
        "default": {"endpoint": "https://example.com"},
    },
)

shared_client = registry.get()
fresh_client = registry.resolve("default?endpoint=https://api.example.com")
```

**Key methods**

- `register(name, object)` / `unregister(name)`: object を登録・解除
- `get(name=None)`: object を取得し、未生成の場合は生成して保持
- `create(name, **kwargs)`: 設定から新しい object を生成
- `resolve(input=None, **kwargs)`: instance または設定 specifier を解決して新しい object を生成
- `register_config(name, config)` / `unregister_config(name)`: runtime の設定を登録・解除
- `list_names()` / `list_aliases()`: 利用可能な名前と alias を取得
- `clear()` / `clear_configs()`: runtime の object または設定を削除
