# kiarina-utils-file

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-utils-file.svg)](https://badge.fury.io/py/kiarina-utils-file)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-file.svg)](https://pypi.org/project/kiarina-utils-file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] これは何？
> sync / async の file I/O と、encoding、MIME type、拡張子の検出を提供するパッケージ。

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

content による MIME type 検出には `mime` extra を使用します。

```bash
pip install "kiarina-utils-file[mime]"
```

## Features

- **Reading and Writing Files**
  Text、binary、JSON、YAML を sync / async API で読み書きできます。
- **Reading Markdown Front Matter**
  Markdown 本文と YAML front matter を分けて取得できます。
- **Handling File Data**
  file path、MIME type、binary、text、hash、拡張子をひとつの object で扱えます。
- **Detecting File Metadata**
  binary data や file name から encoding、MIME type、拡張子を検出できます。

### Reading and Writing Files

存在しない file を読むと `None` を返します。`default` を渡すと、代わりにその値を返します。

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

async API は `kiarina.utils.file.asyncio` から import します。

```python
from kiarina.utils.file.asyncio import read_text, write_text

text = await read_text("message.txt", default="")
await write_text("copy.txt", text)
```

write operation は lock を取得し、同じ directory に作成した一時 file を atomic replace します。

### Reading Markdown Front Matter

`read_markdown` は YAML front matter を `metadata`、残りを `content` として返します。front matter がない場合や不正な場合、`metadata` は空の dictionary になります。

```python
from kiarina.utils.file import read_markdown

document = read_markdown("article.md")
if document is not None:
    print(document.metadata.get("title"))
    print(document.content)
```

文字列は `MarkdownContent.from_text` で同じ形式に変換できます。

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

`MIMEBlob` は MIME type と data を保持します。`FileBlob` はそれに file path を加えます。

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

`raw_data` と `raw_text` は同時に指定できません。`MIMEBlob` は指定された MIME type と data の一致を検証しません。

### Detecting File Metadata

MIME type は file name の拡張子を優先し、検出できない場合に content を使用します。

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

`nkf` が利用可能な日本語環境では、encoding 検出に自動で使用されます。`use_nkf` で明示的に切り替えられます。

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

file が存在しない場合は `default` を返します。directory を指定した場合は `IsADirectoryError`、JSON または YAML の top-level type が関数名と一致しない場合は `TypeError` を送出します。

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

`write_file` の `file_path` を省略すると `file_blob.file_path` を使用します。`remove_file` は file が存在しない場合も正常終了します。

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

`mime_blob` を省略する場合は `mime_type` と、`raw_data` または `raw_text` を指定します。`replace` は新しい `FileBlob` を返します。

#### `MarkdownContent`

```python
class MarkdownContent(NamedTuple):
    content: str
    metadata: dict[str, Any]

    @classmethod
    def from_text(cls, text: str) -> MarkdownContent: ...
```

### `kiarina.utils.file.asyncio`

`kiarina.utils.file` と同じ class を公開し、read、write、remove operation を async function として提供します。引数と default は sync API と同じです。

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

`detect_mime_type` では `raw_data` と `stream` を同時に指定できません。`options` で MIME alias、extension mapping、複合拡張子を上書きできます。

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

`SettingsManager[MIMESettings]` instance です。`KIARINA_UTILS_MIME_` prefix の環境変数で custom MIME types、alias、hash algorithm を設定できます。

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

`extract_extension` は query と fragment を除去し、`.tar.gz` などの複合拡張子を優先します。`settings_manager` は `SettingsManager[ExtSettings]` instance で、`KIARINA_UTILS_EXT_` prefix を使用します。

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

`detect_encoding` は nkf、Charset Normalizer、fallback encoding の順に試します。`decode_binary_to_text` は改行を `\n` に統一します。`settings_manager` は `SettingsManager[EncodingSettings]` instance で、`KIARINA_UTILS_ENCODING_` prefix を使用します。

## License

[MIT License](../../LICENSE)
