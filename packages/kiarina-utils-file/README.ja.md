# kiarina-utils-file

[English](README.md) | 日本語

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE]
> sync / async の file I/O と、encoding、MIME type、拡張子の検出を提供します。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [aiofiles](https://github.com/Tinche/aiofiles) | `>=24.1.0` | [Apache-2.0](https://github.com/Tinche/aiofiles/blob/main/LICENSE) |
| [Charset Normalizer](https://github.com/jawah/charset_normalizer) | `>=3.4.3` | [MIT](https://github.com/jawah/charset_normalizer/blob/master/LICENSE) |
| [filelock](https://github.com/tox-dev/py-filelock) | `>=3.19.1` | [Unlicense](https://github.com/tox-dev/py-filelock/blob/main/LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |
| [PyYAML](https://github.com/yaml/pyyaml) | `>=6.0.2` | [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-utils-file
```

content による MIME type 検出には optional dependency を追加します。

```bash
pip install "kiarina-utils-file[mime]"
```

## Features

- Text、binary、JSON、YAML、Markdown の sync / async I/O
- lock と atomic replace を使う file write
- encoding、MIME type、複合拡張子の検出
- file data を扱う `FileBlob` と `MIMEBlob`

```python
from kiarina.utils.file import read_json_dict, write_text

config = read_json_dict("config.json", default={})
write_text("output.txt", "Hello")
```

async API は `kiarina.utils.file.asyncio` から import します。

```python
from kiarina.utils.file.asyncio import read_text

text = await read_text("input.txt", default="")
```

## API Reference

### `kiarina.utils.file`

```python
class FileBlob:
    def __init__(
        self,
        file_path: str | os.PathLike[str],
        mime_blob: MIMEBlob | None = None,
        *,
        mime_type: str | None = None,
        raw_data: bytes | None = None,
        raw_text: str | None = None,
    ) -> None: ...

class MarkdownContent(NamedTuple):
    content: str
    metadata: dict[str, Any]

    @classmethod
    def from_text(cls, text: str) -> MarkdownContent: ...

def read_file(...) -> FileBlob | None: ...
def read_markdown(...) -> MarkdownContent | None: ...
def write_file(...) -> None: ...
def read_binary(...) -> bytes | None: ...
def read_text(...) -> str | None: ...
def read_json_dict(...) -> dict[str, Any] | None: ...
def read_json_list(...) -> list[Any] | None: ...
def read_yaml_dict(...) -> dict[str, Any] | None: ...
def read_yaml_list(...) -> list[Any] | None: ...
def remove_file(...) -> None: ...
def write_binary(...) -> None: ...
def write_text(...) -> None: ...
def write_json_dict(...) -> None: ...
def write_json_list(...) -> None: ...
def write_yaml_dict(...) -> None: ...
def write_yaml_list(...) -> None: ...
```

`FileBlob` は `file_path`、`mime_blob`、`mime_type`、`raw_data`、`raw_text`、`raw_base64_str`、`raw_base64_url`、`hash_string`、`ext`、`hashed_file_name` property と、`is_binary()`、`is_text()`、`replace()` を提供します。

### `kiarina.utils.file.asyncio`

`kiarina.utils.file` と同じ read / write / remove API の async 版を提供します。

### `kiarina.utils.mime`

```python
class MIMEBlob:
    def __init__(
        self,
        mime_type: str,
        raw_data: bytes | None = None,
        *,
        raw_text: str | None = None,
    ) -> None: ...

def apply_mime_alias(mime_type: str, *, mime_aliases: dict[str, str] | None = None) -> str: ...
def create_mime_blob(raw_data: bytes, *, fallback_mime_type: str = "application/octet-stream") -> MIMEBlob: ...
def detect_mime_type(...) -> str | None: ...
```

`MIMEBlob` は `mime_type`、`raw_data`、`raw_text`、`raw_base64_str`、`raw_base64_url`、`hash_string`、`ext`、`hashed_file_name` property と、`is_binary()`、`is_text()`、`replace()` を提供します。

### `kiarina.utils.ext`

```python
def detect_extension(mime_type: str, *, custom_extensions: dict[str, str] | None = None, default: str | None = None) -> str | None: ...
def extract_extension(file_name_hint: str, *, default: str | None = None, **kwargs: Unpack[MimeDetectionOptions]) -> str | None: ...
```

### `kiarina.utils.encoding`

```python
def decode_binary_to_text(raw_data: bytes, *, use_nkf: bool | None = None, **kwargs: Any) -> str: ...
def detect_encoding(raw_data: bytes, *, use_nkf: bool | None = None, **kwargs: Any) -> str | None: ...
def get_default_encoding() -> str: ...
def is_binary(raw_data: bytes, *, use_nkf: bool | None = None, **kwargs: Any) -> bool: ...
def normalize_newlines(text: str) -> str: ...
```

各検出 module は `settings_manager` を公開します。設定には `KIARINA_UTILS_ENCODING_`、`KIARINA_UTILS_EXT_`、`KIARINA_UTILS_FILE_`、`KIARINA_UTILS_MIME_` prefix の環境変数を使用できます。

## License

[MIT License](../../LICENSE)
