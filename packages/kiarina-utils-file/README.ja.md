# kiarina-utils-file

[English](README.md) | 日本語

自動エンコーディング検出、MIME type 検出、複数ファイル形式に対応した包括的な Python file I/O library です。

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### 🚀 **Comprehensive File I/O**

- Text、binary、JSON、YAML を扱えます。
- sync / async API の両方を提供します。
- 一時ファイルと lock を使った atomic write に対応します。

### 🔍 **Smart Detection**

- nkf サポートを含む自動エンコーディング検出
- 複数手法による MIME type 検出
- `.tar.gz` のような複合拡張子の扱い

### 📦 **Data Containers**

- **FileBlob**: path と metadata を持つ統一的な file container
- **MIMEBlob**: MIME type つき binary data container
- content hash による名前付け

### 🛡️ **Production Ready**

- default 値による missing file の扱い
- non-blocking I/O と cache を活用した実装
- type hints とテスト

## Installation

```bash
pip install kiarina-utils-file
```

### Optional Dependencies

```bash
pip install kiarina-utils-file[mime]
pip install kiarina-utils-file[all]
```

## Quick Start

### Basic File Operations

```python
import kiarina.utils.file as kf

text = kf.read_text("document.txt", default="")
kf.write_text("output.txt", "Hello, World!")

data = kf.read_binary("image.jpg")
if data:
    kf.write_binary("copy.jpg", data)

config = kf.read_json_dict("config.json", default={})
kf.write_json_dict("output.json", {"key": "value"})
```

### High-Level FileBlob Operations

```python
import kiarina.utils.file as kf

blob = kf.read_file("document.pdf")
if blob:
    print(blob.file_path)
    print(blob.mime_type)
    print(len(blob.raw_data))
```

### Async Operations

```python
import kiarina.utils.file.asyncio as kfa

async def process_files():
    text = await kfa.read_text("large_file.txt")
    await kfa.write_json_dict("result.json", {"processed": True})
```

### MIME Type and Extension Detection

```python
import kiarina.utils.ext as ke
import kiarina.utils.mime as km

mime_type = km.detect_mime_type(file_name_hint="document.md", raw_data=file_data)
extension = ke.extract_extension("archive.tar.gz")
```

### Encoding Detection

```python
import kiarina.utils.encoding as kenc

encoding = kenc.detect_encoding(raw_data)
text = kenc.decode_binary_to_text(raw_data)
```

## Advanced Usage

### Custom Configuration

環境変数でエンコーディング検出、file lock、MIME type 検出などの挙動を調整できます。

### Error Handling

`default` を指定すると、missing file を `None` check なしで扱いやすくできます。JSON decode error などは通常の例外として処理します。

### Performance Considerations

大量の I/O では async API を使うと、待ち時間を効率よく扱えます。

## API Reference

### File Operations

#### Synchronous API (`kiarina.utils.file`)

`read_file`、`write_file`、`read_text`、`write_text`、`read_binary`、`write_binary`、JSON/YAML read/write、`remove_file` を提供します。

#### Asynchronous API (`kiarina.utils.file.asyncio`)

sync API と同等の async 関数を提供します。

### Data Containers

#### FileBlob

file path、MIMEBlob、MIME type、raw data/text などをまとめて扱う container です。

#### MIMEBlob

MIME type つきの binary data container です。

### Utility Functions

#### MIME Type Detection (`kiarina.utils.mime`)

content または file name hint から MIME type を検出します。

#### Extension Detection (`kiarina.utils.ext`)

MIME type や file name から拡張子を扱います。

#### Encoding Detection (`kiarina.utils.encoding`)

binary data の文字エンコーディング検出と text decode を提供します。

## Configuration

### Environment Variables

#### Encoding Detection

`KIARINA_UTILS_ENCODING_*`

#### File Operations

`KIARINA_UTILS_FILE_*`

#### MIME Type Detection

`KIARINA_UTILS_MIME_*`

#### Extension Detection

`KIARINA_UTILS_EXT_*`

## Requirements

Python 3.12 以上が必要です。

## Development

### Prerequisites

Python 3.12+、uv、mise が必要です。

### Setup

```bash
mise run setup
```

### Running Tests

```bash
mise run package:test kiarina-utils-file
mise run package:test kiarina-utils-file --coverage
```

### Code Quality

```bash
mise run package:format kiarina-utils-file
mise run package:lint kiarina-utils-file
mise run package:check kiarina-utils-file
```

## Performance

### Benchmarks

I/O intensive な処理では async API の利用を推奨します。

### Memory Usage

大きな binary を扱う場合は、必要な範囲で FileBlob / MIMEBlob を保持してください。

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Contributing

### Guidelines

issue や pull request は歓迎します。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)

## Changelog

変更履歴は [CHANGELOG.md](CHANGELOG.md) を参照してください。

## Support

質問や不具合報告は GitHub Issues を利用してください。

