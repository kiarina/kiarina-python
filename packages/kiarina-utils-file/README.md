# kiarina-utils-file

[![PyPI version](https://badge.fury.io/py/kiarina-utils-file.svg)](https://badge.fury.io/py/kiarina-utils-file)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-file.svg)](https://pypi.org/project/kiarina-utils-file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> A package for synchronous and asynchronous file I/O plus encoding, MIME type, and extension detection.

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

### Optional Dependencies

Use the `mime` extra for content-based MIME type detection.

```bash
pip install "kiarina-utils-file[mime]"
```

## Features

- **Reading and Writing Files**
  Read and write text, binary, JSON, and YAML with synchronous or asynchronous APIs.
- **Reading Markdown Front Matter**
  Separate Markdown content from YAML front matter.
- **Handling File Data**
  Handle a file path, MIME type, binary data, text, hash, and extension in one object.
- **Detecting File Metadata**
  Detect encoding, MIME type, and extensions from binary data or a file name.

### Reading and Writing Files

Read operations return `None` when a file does not exist. Pass `default` to return another value instead.

```python
from kiarina.utils.file import (
    read_binary,
    read_json_dict,
    read_text,
    read_yaml_dict,
    write_binary,
    write_json_dict,
    write_text,
    write_yaml_dict,
)

text = read_text("message.txt", default="")
data = read_binary("image.png", default=b"")
config = read_json_dict("config.json", default={})
metadata = read_yaml_dict("metadata.yaml", default={})

write_text("message.txt", text)
write_binary("image.png", data)
write_json_dict("config.json", config)
write_yaml_dict("metadata.yaml", metadata)
```

Import asynchronous APIs from `kiarina.utils.file.asyncio`.

```python
from kiarina.utils.file.asyncio import read_text, write_text

text = await read_text("message.txt", default="")
await write_text("copy.txt", text)
```

Write operations acquire a lock and atomically replace the target with a temporary file created in the same directory.

### Reading Markdown Front Matter

`read_markdown` returns YAML front matter as `metadata` and the remaining text as `content`. `metadata` is an empty dictionary when front matter is missing or invalid.

```python
from kiarina.utils.file import read_markdown

document = read_markdown("article.md")
if document is not None:
    print(document.metadata.get("title"))
    print(document.content)
```

Use `MarkdownContent.from_text` to parse a string in the same format.

```python
from kiarina.utils.file import MarkdownContent

document = MarkdownContent.from_text(
    """---
title: Example
---
# Content
"""
)
```

### Handling File Data

`MIMEBlob` stores a MIME type and data. `FileBlob` adds a file path.

```python
from kiarina.utils.file import FileBlob, write_file
from kiarina.utils.mime import MIMEBlob

mime_blob = MIMEBlob("text/plain", raw_text="Hello")
file_blob = FileBlob("message.txt", mime_blob)

print(file_blob.raw_data)
print(file_blob.raw_base64_url)
print(file_blob.hash_string)
print(file_blob.ext)

write_file(file_blob)
```

`raw_data` and `raw_text` are mutually exclusive. `MIMEBlob` does not validate whether the supplied MIME type matches the data.

### Detecting File Metadata

MIME type detection prioritizes the file name extension and falls back to content.

```python
from kiarina.utils.encoding import decode_binary_to_text, detect_encoding
from kiarina.utils.ext import detect_extension, extract_extension
from kiarina.utils.mime import detect_mime_type

encoding = detect_encoding(raw_data)
text = decode_binary_to_text(raw_data)

mime_type = detect_mime_type(
    file_name_hint="document.md",
    raw_data=raw_data,
)
extension = detect_extension("application/json")
archive_extension = extract_extension("archive.tar.gz")
```

In Japanese environments, encoding detection automatically uses `nkf` when available. Pass `use_nkf` to select this behavior explicitly.

## API Reference

### `kiarina.utils.file`

```python
from kiarina.utils.file import (
    FileBlob,
    MarkdownContent,
    read_binary,
    read_file,
    read_json_dict,
    read_json_list,
    read_markdown,
    read_text,
    read_yaml_dict,
    read_yaml_list,
    remove_file,
    write_binary,
    write_file,
    write_json_dict,
    write_json_list,
    write_text,
    write_yaml_dict,
    write_yaml_list,
)
```

#### Read operations

```python
def read_file(
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob | None = None,
) -> FileBlob | None: ...

def read_markdown(
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> MarkdownContent | None: ...

def read_binary(
    file_path: str | os.PathLike[str],
    *,
    default: bytes | None = None,
) -> bytes | None: ...

def read_text(
    file_path: str | os.PathLike[str],
    *,
    default: str | None = None,
) -> str | None: ...

def read_json_dict(
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None: ...

def read_json_list(
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> list[Any] | None: ...

def read_yaml_dict(
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None: ...

def read_yaml_list(
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> list[Any] | None: ...
```

These functions return `default` when the file does not exist. They raise `IsADirectoryError` for a directory and `TypeError` when the top-level JSON or YAML type does not match the function name.

#### Write and remove operations

```python
def write_file(
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> None: ...

def write_binary(
    file_path: str | os.PathLike[str],
    raw_data: bytes,
) -> None: ...

def write_text(
    file_path: str | os.PathLike[str],
    raw_text: str,
) -> None: ...

def write_json_dict(
    file_path: str | os.PathLike[str],
    json_dict: dict[str, Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None: ...

def write_json_list(
    file_path: str | os.PathLike[str],
    json_list: list[Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None: ...

def write_yaml_dict(
    file_path: str | os.PathLike[str],
    yaml_dict: dict[str, Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> None: ...

def write_yaml_list(
    file_path: str | os.PathLike[str],
    yaml_list: list[Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> None: ...

def remove_file(file_path: str | os.PathLike[str]) -> None: ...
```

`write_file` uses `file_blob.file_path` when `file_path` is omitted. `remove_file` succeeds when the file does not exist.

#### `FileBlob`

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

    @property
    def file_path(self) -> str: ...

    @property
    def mime_blob(self) -> MIMEBlob: ...

    @property
    def mime_type(self) -> str: ...

    @property
    def raw_data(self) -> bytes: ...

    @property
    def raw_text(self) -> str: ...

    @property
    def raw_base64_str(self) -> str: ...

    @property
    def raw_base64_url(self) -> str: ...

    @property
    def hash_string(self) -> str: ...

    @property
    def ext(self) -> str: ...

    @property
    def hashed_file_name(self) -> str: ...

    def is_binary(self) -> bool: ...

    def is_text(self) -> bool: ...

    def replace(
        self,
        *,
        file_path: str | os.PathLike[str] | None = None,
        mime_blob: MIMEBlob | None = None,
        mime_type: str | None = None,
        raw_data: bytes | None = None,
        raw_text: str | None = None,
    ) -> Self: ...
```

When `mime_blob` is omitted, provide `mime_type` and either `raw_data` or `raw_text`. `replace` returns a new `FileBlob`.

#### `MarkdownContent`

```python
class MarkdownContent(NamedTuple):
    content: str
    metadata: dict[str, Any]

    @classmethod
    def from_text(cls, text: str) -> MarkdownContent: ...
```

### `kiarina.utils.file.asyncio`

This module exports the same classes as `kiarina.utils.file` and provides asynchronous read, write, and remove operations. Parameters and defaults match the synchronous API.

```python
async def read_file(
    file_path: str | os.PathLike[str],
    *,
    fallback_mime_type: str = "application/octet-stream",
    default: FileBlob | None = None,
) -> FileBlob | None: ...

async def read_markdown(
    file_path: str | os.PathLike[str],
    *,
    default: MarkdownContent | None = None,
) -> MarkdownContent | None: ...

async def read_binary(
    file_path: str | os.PathLike[str],
    *,
    default: bytes | None = None,
) -> bytes | None: ...

async def read_text(
    file_path: str | os.PathLike[str],
    *,
    default: str | None = None,
) -> str | None: ...

async def read_json_dict(
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None: ...

async def read_json_list(
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> list[Any] | None: ...

async def read_yaml_dict(
    file_path: str | os.PathLike[str],
    *,
    default: dict[str, Any] | None = None,
) -> dict[str, Any] | None: ...

async def read_yaml_list(
    file_path: str | os.PathLike[str],
    *,
    default: list[Any] | None = None,
) -> list[Any] | None: ...

async def write_file(
    file_blob: FileBlob,
    file_path: str | os.PathLike[str] | None = None,
) -> None: ...

async def write_binary(
    file_path: str | os.PathLike[str],
    raw_data: bytes,
) -> None: ...

async def write_text(
    file_path: str | os.PathLike[str],
    raw_text: str,
) -> None: ...

async def write_json_dict(
    file_path: str | os.PathLike[str],
    json_dict: dict[str, Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None: ...

async def write_json_list(
    file_path: str | os.PathLike[str],
    json_list: list[Any],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None: ...

async def write_yaml_dict(
    file_path: str | os.PathLike[str],
    yaml_dict: dict[str, Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> None: ...

async def write_yaml_list(
    file_path: str | os.PathLike[str],
    yaml_list: list[Any],
    *,
    allow_unicode: bool = True,
    sort_keys: bool = False,
) -> None: ...

async def remove_file(file_path: str | os.PathLike[str]) -> None: ...
```

### `kiarina.utils.mime`

```python
from kiarina.utils.mime import (
    MIMEBlob,
    MimeDetectionOptions,
    apply_mime_alias,
    create_mime_blob,
    detect_mime_type,
    settings_manager,
)
```

#### Functions

```python
def apply_mime_alias(
    mime_type: str,
    *,
    mime_aliases: dict[str, str] | None = None,
) -> str: ...

def create_mime_blob(
    raw_data: bytes,
    *,
    fallback_mime_type: str = "application/octet-stream",
) -> MIMEBlob: ...

def detect_mime_type(
    *,
    file_name_hint: str | os.PathLike[str] | None = None,
    raw_data: bytes | None = None,
    stream: BinaryIO | None = None,
    options: MimeDetectionOptions | None = None,
    default: str | None = None,
) -> str | None: ...
```

`raw_data` and `stream` are mutually exclusive in `detect_mime_type`. Use `options` to override MIME aliases, extension mappings, and multi-part extensions.

#### `MIMEBlob`

```python
class MIMEBlob:
    def __init__(
        self,
        mime_type: str,
        raw_data: bytes | None = None,
        *,
        raw_text: str | None = None,
    ) -> None: ...

    @property
    def mime_type(self) -> str: ...

    @property
    def raw_data(self) -> bytes: ...

    @property
    def raw_text(self) -> str: ...

    @property
    def raw_base64_str(self) -> str: ...

    @property
    def raw_base64_url(self) -> str: ...

    @property
    def hash_string(self) -> str: ...

    @property
    def ext(self) -> str: ...

    @property
    def hashed_file_name(self) -> str: ...

    def is_binary(self) -> bool: ...

    def is_text(self) -> bool: ...

    def replace(
        self,
        *,
        mime_type: str | None = None,
        raw_data: bytes | None = None,
        raw_text: str | None = None,
    ) -> Self: ...
```

#### `MimeDetectionOptions`

```python
class MimeDetectionOptions(TypedDict, total=False):
    mime_aliases: NotRequired[dict[str, str]]
    custom_mime_types: NotRequired[dict[str, str]]
    multi_extensions: NotRequired[set[str]]
    archive_extensions: NotRequired[set[str]]
    compression_extensions: NotRequired[set[str]]
    encryption_extensions: NotRequired[set[str]]
```

#### `settings_manager`

A `SettingsManager[MIMESettings]` instance. Configure custom MIME types, aliases, and the hash algorithm with environment variables using the `KIARINA_UTILS_MIME_` prefix.

### `kiarina.utils.ext`

```python
from kiarina.utils.ext import (
    detect_extension,
    extract_extension,
    settings_manager,
)
```

```python
def detect_extension(
    mime_type: str,
    *,
    custom_extensions: dict[str, str] | None = None,
    default: str | None = None,
) -> str | None: ...

def extract_extension(
    file_name_hint: str | os.PathLike[str],
    *,
    multi_extensions: set[str] | None = None,
    archive_extensions: set[str] | None = None,
    compression_extensions: set[str] | None = None,
    encryption_extensions: set[str] | None = None,
    default: str | None = None,
) -> str | None: ...
```

`extract_extension` removes query strings and fragments and prioritizes multi-part extensions such as `.tar.gz`. `settings_manager` is a `SettingsManager[ExtSettings]` instance using the `KIARINA_UTILS_EXT_` prefix.

### `kiarina.utils.encoding`

```python
from kiarina.utils.encoding import (
    decode_binary_to_text,
    detect_encoding,
    get_default_encoding,
    is_binary,
    normalize_newlines,
    settings_manager,
)
```

```python
def decode_binary_to_text(
    raw_data: bytes,
    *,
    use_nkf: bool | None = None,
    fallback_encodings: list[str] | None = None,
    default_encoding: str | None = None,
) -> str: ...

def detect_encoding(
    raw_data: bytes,
    *,
    use_nkf: bool | None = None,
    confidence_threshold: float | None = None,
    fallback_encodings: list[str] | None = None,
) -> str | None: ...

def get_default_encoding() -> str: ...

def is_binary(
    raw_data: bytes,
    *,
    use_nkf: bool | None = None,
    fallback_encodings: list[str] | None = None,
) -> bool: ...

def normalize_newlines(text: str) -> str: ...
```

`detect_encoding` tries nkf, Charset Normalizer, and fallback encodings in that order. `decode_binary_to_text` normalizes newlines to `\n`. `settings_manager` is a `SettingsManager[EncodingSettings]` instance using the `KIARINA_UTILS_ENCODING_` prefix.

## License

[MIT License](../../LICENSE)
