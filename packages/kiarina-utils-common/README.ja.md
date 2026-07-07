# kiarina-utils-common

[![PyPI version](https://badge.fury.io/py/kiarina-utils-common.svg)](https://badge.fury.io/py/kiarina-utils-common)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-common.svg)](https://pypi.org/project/kiarina-utils-common/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] これは何？
> 軽量な設定解決・動的 import・registry 基盤を提供するパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-utils-common
```

## Features

- **Implementing a Plugin System**
  設定された import path から実装を選択し、動的に生成するプラグインシステムを構築できます。
- **Managing a Singleton**
  設定を解決して生成した object を保持し、再利用することができます。

### Implementing a Plugin System

ComponentRegistry を使うと、設定された import path から実装を選択・生成するプラグイン機構を構築できます。
下記の例では、[pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) を使用しています。

```sh
sample/
  hoge/
    _instances/
      hoge_registry.py
    _services/
      base_hoge.py
    _types/
      hoge.py
      hoge_name.py
      hoge_alias.py
      hoge_specifier.py
    __init__.py
    _settings.py
  hoge_impl/
    vanilla/
      _helpers/
        create_vanilla_hoge.py
      _services/
        vanilla_hoge.py
      __init__.py
      _settings.py
```

**抽象を定義:**
```python
# sample/hoge/_types/hoge_name.py
HogeName: TypeAlias = str

# sample/hoge/_types/hoge_alias.py
HogeAlias: TypeAlias = str

# sample/hoge/_types/hoge_specifier.py
HogeSpecifier: TypeAlias = str
"""{HogeName}[?{ConfigString}]"""

# sample/hoge/_types/hoge.py
@runtime_checkable
class Hoge(Protocol):
    name: HogeName
    def hello(self) -> None: ...

# sample/hoge/_services/base_hoge.py
class BaseHoge(Hoge):
    def __init__(self) -> None:
        self._name: HogeName | None = None

    @property
    def name(self) -> HogeName:
        if self._name is None:
            raise ValueError("name is not set")
        return self._name

    @name.setter
    def name(self, value: HogeName) -> None:
        self._name = value

# sample/hoge/_settings.py
class HogeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SAMPLE_HOGE_",
        extra="ignore",
    )

    default: HogeSpecifier = "vanilla"

    aliases: dict[HogeAlias, HogeName] = Field(default_factory=dict)

    presets: dict[HogeName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "sample.hoge_impl.vanilla:create_vanilla_hoge",
        }
    )

    customs: dict[HogeName, ImportPath] = Field(default_factory=dict)

settings_manager = SettingsManager(HogeSettings)

# sample/hoge/_instances/hoge_registry.py
def _factory_wrapper(
    factory: ComponentFactory[Hoge],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Hoge:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance

hoge_registry = ComponentRegistry[Hoge](
    expected_type=cast(type[Hoge], Hoge),
    component_label="Hoge",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)

# sample/hoge/__init__.py
__all__ = [
    "BaseHoge",
    "Hoge",
    "HogeName",
    "HogeAlias",
    "HogeSpecifier",
    "settings_manager",
    "hoge_registry",
]
```

**実装を定義:**
```python
# sample/hoge_impl/vanilla/_settings.py
class VanillaHogeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SAMPLE_HOGE_VANILLA_",
        extra="ignore",
    )
    message: str = "Hello from VanillaHoge!"

settings_manager = SettingsManager(VanillaHogeSettings)

# sample/hoge_impl/vanilla/_services/vanilla_hoge.py
class VanillaHoge(BaseHoge):
    def __init__(self, settings: VanillaHogeSettings) -> None:
        super().__init__()
        self.settings: VanillaHogeSettings = settings

    def hello(self) -> None:
        print(self.settings.message)

# sample/hoge_impl/vanilla/_helpers/create_vanilla_hoge.py
def create_vanilla_hoge(**kwargs: Any) -> VanillaHoge:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = VanillaHogeSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return VanillaHoge(settings)

# sample/hoge_impl/vanilla/__init__.py
__all__ = ["create_vanilla_hoge", "VanillaHoge", "settings_manager"]
```

**使い方:**
```python
hoge = hoge_registry.resolve()  # default を取得
hoge = hoge_registry.resolve("vanilla")  # preset を取得
hoge = hoge_registry.resolve("vanilla?message=Bye")  # ConfigString で上書き
hoge.hello()
```

### Managing a Singleton

ObjectRegistry を使うと、設定を解決して生成した object を保持し、再利用することができます。

レジストリを定義:
```python
from typing import Any

from kiarina.utils.object_registry import ObjectRegistry
from rich.console import Console


def _factory(name: str, config: dict[str, Any]) -> Console:
    return Console(**config)

console_registry = ObjectRegistry[Console, dict[str, Any]](
    expected_type=Console,
    object_label="Console",
    get_default=lambda: "default",
    get_presets=lambda: {
        "default": {"stderr": True, "highlight": False},
    },
    factory=_factory,
)
```

使い方:
```python
console1 = console_registry.get()  # default を取得
console2 = console_registry.get("default")  # preset を取得
console3 = console_registry.resolve("default?highlight=True")  # ConfigString で上書き

console1.print("Hello, World!")
assert console1 is console_registry.get()  # 同じ object を返す
```

## API Reference

### `kiarina.utils.common`

```python
from kiarina.utils.common import (
    ConfigString,
    ImportPath,
    download_file,
    import_object,
    parse_config_string,
)
```

#### `download_file`

```python
def download_file(
    url: str,
    sha256: str,
    cache_path: os.PathLike[str] | str,
) -> Path: ...
```

`cache_path` にファイルが存在しない場合だけ、ファイルをダウンロードします。

ファイルは同じ directory の一時ファイルへ書き込み、SHA-256 で検証した後、atomic に `cache_path` へ配置します。既存ファイルは hash 検証せずに再利用します。

- `RuntimeError`: ダウンロードに失敗した場合、または SHA-256 digest が一致しない場合

#### `import_object`

```python
def import_object(import_path: ImportPath) -> Any: ...
```

`module_name:object_name` 形式の import path から object を import して返します。

- `ValueError`: import path の形式が不正な場合
- `ImportError`: module を import できない場合
- `AttributeError`: module 内に object が存在しない場合

#### `parse_config_string`

```python
def parse_config_string(
    config_str: ConfigString,
    *,
    separator: str = "&",
    key_value_separator: str = "=",
    nested_separator: str = ".",
    brackets: str = "()",
) -> dict[str, Any]: ...
```

設定文字列を nested dictionary に変換します。

値は `bool`、`int`、`float` へ自動変換されます。value のない key は `None` になり、数値の nested key は list の index として扱われます。`brackets` で囲まれた value は区切り文字を含めることができ、型変換されません。

```python
parse_config_string(
    "enabled=true&ports.0=8000&ports.1=8001&plugin=(mock?delay=0.1)"
)
# {
#     "enabled": True,
#     "ports": [8000, 8001],
#     "plugin": "mock?delay=0.1",
# }
```

`brackets` が2文字でない場合、開き文字と閉じ文字が同じ場合、区切り文字と競合する場合、または設定文字列内の bracket が対応していない場合は `ValueError` を送出します。

#### Type aliases

```python
type ConfigString = str
ImportPath: TypeAlias = str
```

| Type | Format |
| --- | --- |
| `ConfigString` | `key=value&key2=value2` |
| `ImportPath` | `module_name:object_name` |

### `kiarina.utils.config_registry`

```python
from kiarina.utils.config_registry import (
    ConfigAlias,
    ConfigName,
    ConfigRegistry,
    ConfigSpecifier,
    ResolvedConfig,
)
```

#### `ConfigRegistry`

名前、alias、default を使って設定を管理し、`ConfigString` または keyword argument による上書きを適用して解決します。取得した設定は deep copy されるため、登録元の設定は変更されません。

```python
class ConfigRegistry(Generic[T]):
    def __init__(
        self,
        *,
        config_label: str = "Config",
        get_default: Callable[[], ConfigSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ConfigAlias, ConfigName]] | None = None,
        get_presets: Callable[[], dict[ConfigName, T]] | None = None,
        get_customs: Callable[[], dict[ConfigName, T]] | None = None,
        configure: Callable[[T, dict[str, Any]], T] | None = None,
    ) -> None: ...

    def get_default(self) -> ConfigSpecifier | None: ...

    def get_aliases(self) -> dict[ConfigAlias, ConfigName]: ...

    def list_aliases(self) -> list[ConfigAlias]: ...

    def list_names(self) -> list[ConfigName]: ...

    def register(self, config_name: ConfigName, config: T) -> None: ...

    def unregister(self, config_name: ConfigName) -> None: ...

    def is_registered(self, config_name: ConfigName) -> bool: ...

    def clear(self) -> None: ...

    def get(
        self,
        config_specifier: ConfigSpecifier | None = None,
        **kwargs: Any,
    ) -> T: ...

    def resolve(
        self,
        config_specifier: ConfigSpecifier | None = None,
        **kwargs: Any,
    ) -> ResolvedConfig[T]: ...
```

`get()` と `resolve()` は、runtime registration、custom、preset の順に設定を探索します。`configure` を省略した場合は Pydantic `BaseModel` と `dict` を上書きできます。それ以外の型を上書きするには `configure` を指定します。

#### `ResolvedConfig`

```python
class ResolvedConfig(NamedTuple, Generic[T]):
    name: ConfigName
    config: T
```

解決後の設定名と設定値を保持します。

#### Type aliases

```python
ConfigAlias: TypeAlias = str
ConfigName: TypeAlias = str
ConfigSpecifier: TypeAlias = str
```

`ConfigSpecifier` は `{ConfigName|ConfigAlias}[?{ConfigString}]` 形式の文字列です。

### `kiarina.utils.component_registry`

```python
from kiarina.utils.component_registry import (
    ComponentAlias,
    ComponentFactory,
    ComponentInput,
    ComponentName,
    ComponentRegistry,
    ComponentSpecifier,
)
```

#### `ComponentRegistry`

class や factory を名前で管理し、必要なときに新しい instance を生成します。import path で定義された preset や custom component も利用できます。

```python
class ComponentRegistry(Generic[T]):
    def __init__(
        self,
        *,
        expected_type: type[T],
        component_label: str = "Component",
        get_default: Callable[[], ComponentSpecifier | None] | None = None,
        get_aliases: Callable[
            [], dict[ComponentAlias, ComponentName]
        ] | None = None,
        get_presets: Callable[
            [], dict[ComponentName, ImportPath]
        ] | None = None,
        get_customs: Callable[
            [], dict[ComponentName, ImportPath]
        ] | None = None,
        factory_wrapper: Callable[
            [ComponentFactory[T], ComponentName, Any], T
        ] | None = None,
    ) -> None: ...

    def get_default(self) -> ComponentSpecifier | None: ...

    def get_aliases(self) -> dict[ComponentAlias, ComponentName]: ...

    def list_aliases(self) -> list[ComponentAlias]: ...

    def list_names(self) -> list[ComponentName]: ...

    def register(
        self,
        component_name: ComponentName,
        factory: ComponentFactory[T],
    ) -> None: ...

    def unregister(self, component_name: ComponentName) -> None: ...

    def get(
        self,
        component_name: ComponentName,
    ) -> ComponentFactory[T] | None: ...

    def clear(self) -> None: ...

    def create(
        self,
        component_name: ComponentName,
        *args: Any,
        **kwargs: Any,
    ) -> T: ...

    def resolve(
        self,
        component_input: ComponentInput[T] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T: ...
```

`create()` と `resolve()` は常に新しい instance を生成し、`expected_type` に一致しない場合は `ValueError` を送出します。factory は runtime registration、custom、preset の順に探索されます。

#### Type aliases

```python
ComponentAlias: TypeAlias = str
ComponentFactory: TypeAlias = Callable[..., T]
ComponentInput: TypeAlias = T | ComponentSpecifier
ComponentName: TypeAlias = str
ComponentSpecifier: TypeAlias = str
```

`ComponentSpecifier` は `{ComponentName|ComponentAlias}[?{ConfigString}]` 形式の文字列です。

### `kiarina.utils.object_registry`

```python
from kiarina.utils.object_registry import (
    ObjectAlias,
    ObjectFactory,
    ObjectInput,
    ObjectName,
    ObjectRegistry,
    ObjectSpecifier,
)
```

#### `ObjectRegistry`

`ConfigRegistry` で設定を解決し、その設定から object を生成します。`get()` は生成した object を保持して再利用し、`create()` と `resolve()` は毎回新しい object を生成します。

```python
class ObjectRegistry(Generic[TObject, TConfig]):
    def __init__(
        self,
        *,
        expected_type: type[TObject],
        object_label: str = "Object",
        get_default: Callable[[], ObjectSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ObjectAlias, ObjectName]] | None = None,
        get_presets: Callable[[], dict[ObjectName, TConfig]] | None = None,
        get_customs: Callable[[], dict[ObjectName, TConfig]] | None = None,
        configure: Callable[[TConfig, dict[str, Any]], TConfig] | None = None,
        factory: ObjectFactory[TObject, TConfig] | None = None,
    ) -> None: ...

    def get_default(self) -> ObjectSpecifier | None: ...

    def get_aliases(self) -> dict[ObjectAlias, ObjectName]: ...

    def register_config(
        self,
        object_name: ObjectName,
        config: TConfig,
    ) -> None: ...

    def unregister_config(self, object_name: ObjectName) -> None: ...

    def clear_configs(self) -> None: ...

    def is_config_registered(self, object_name: ObjectName) -> bool: ...

    def get_config(
        self,
        object_specifier: ObjectSpecifier | None = None,
    ) -> TConfig: ...

    def list_aliases(self) -> list[ObjectAlias]: ...

    def list_names(self) -> list[ObjectName]: ...

    def register(self, object_name: ObjectName, obj: TObject) -> None: ...

    def unregister(self, object_name: ObjectName) -> None: ...

    def clear(self) -> None: ...

    def is_registered(self, object_name: ObjectName) -> bool: ...

    def get(
        self,
        object_name: ObjectName | ObjectAlias | None = None,
    ) -> TObject: ...

    def create(
        self,
        object_name: ObjectName,
        **kwargs: Any,
    ) -> TObject: ...

    def resolve(
        self,
        object_input: ObjectInput[TObject] | None = None,
        **kwargs: Any,
    ) -> TObject: ...
```

`register()` と object の生成時には、値が `expected_type` に一致することを検証します。`get()` は `ConfigString` を含む specifier を受け付けません。設定を上書きして新しい object を生成する場合は `create()` または `resolve()` を使用します。

#### `ObjectFactory`

```python
class ObjectFactory(Protocol[TObject_co, TConfig_contra]):
    def __call__(
        self,
        object_name: ObjectName,
        config: TConfig_contra,
        /,
    ) -> TObject_co: ...
```

`ObjectRegistry` が解決した object 名と設定を受け取り、object を生成する callable の型です。

#### Type aliases

```python
ObjectAlias: TypeAlias = str
ObjectInput: TypeAlias = TObject | ObjectSpecifier
ObjectName: TypeAlias = str
ObjectSpecifier: TypeAlias = str
```

`ObjectSpecifier` は `{ObjectName|ObjectAlias}[?{ConfigString}]` 形式の文字列です。
