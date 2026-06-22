# kiarina-utils-common

[English](README.md) | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-utils-common.svg)](https://badge.fury.io/py/kiarina-utils-common)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-common.svg)](https://pypi.org/project/kiarina-utils-common/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

kiarina namespace packages 向けの共通ユーティリティ関数です。

## Installation

```bash
pip install kiarina-utils-common
```

## Features

### Dynamic Object Import

import path 文字列からクラス、関数、定数などを動的に import します。plugin system や動的ロードで便利です。

```python
from kiarina.utils.common import import_object

parse_fn = import_object("kiarina.utils.common:parse_config_string")
result = parse_fn("key=value")
```

### Configuration String Parser

設定文字列を、型変換つきのネストした dictionary に変換します。

```python
from kiarina.utils.common import parse_config_string

config = parse_config_string("cache.enabled=true&db.port=5432")
# {"cache": {"enabled": True}, "db": {"port": 5432}}

config = parse_config_string("debug&verbose&cache.enabled=true")
# {"debug": None, "verbose": None, "cache": {"enabled": True}}

config = parse_config_string("items.0=first&items.1=second")
# {"items": ["first", "second"]}

config = parse_config_string("vad=(mock?sample_rate=16000&p.0=1.0)&top_k=3")
# {"vad": "mock?sample_rate=16000&p.0=1.0", "top_k": 3}
```

#### Type Conversion

`"true"` / `"false"` は bool、数値文字列は int または float に変換されます。それ以外は str として扱われます。

#### Nested Keys

`.` 区切りでネストした構造を表現できます。

#### Array Indices

数値 key を使うことで list 構造を表現できます。

## API Reference

### `import_object(import_path)`

`module_name:object_name` 形式の import path から object を import して返します。

### `parse_config_string(config_str, *, separator="&", key_value_separator="=", nested_separator=".", brackets="()")`

設定文字列を `dict[str, Any]` に parse します。`brackets` で囲まれた値は区切り文字を含めても 1 つの値として扱われ、型変換も抑制されます。

## License

このプロジェクトは MIT License のもとで公開されています。詳細は [LICENSE](../../LICENSE) を参照してください。

## Contributing

主に個人用途で開発しているプロジェクトですが、issue や pull request は歓迎します。

## Related Packages

- [kiarina-utils-file](../kiarina-utils-file/)

