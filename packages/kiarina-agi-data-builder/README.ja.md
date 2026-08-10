# kiarina-agi-data-builder

[English](README.md) | 日本語

## What is this?

`kiarina-agi-data-builder` は、AI agent の message、event、history、tool info、file info、file segment を組み立てるための package です。

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-audio](../kiarina-agi-audio/) | `>=2.9.0` | MIT |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-data](../kiarina-agi-data/) | `>=2.7.0` | MIT |
| [kiarina-agi-file](../kiarina-agi-file/) | `>=2.8.0` | MIT |
| [kiarina-agi-tool](../kiarina-agi-tool/) | `>=2.12.0` | MIT |
| [kiarina-agi-video](../kiarina-agi-video/) | `>=2.10.0` | MIT |
| [kiarina-i18n](../kiarina-i18n/) | `>=2.3.1` | MIT |
| [kiarina-utils-app](../kiarina-utils-app/) | `>=2.4.0` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.8.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7,<3` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1,<3` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |
| [PyYAML](https://github.com/yaml/pyyaml) | `>=6.0.2` | MIT |

### Optional Dependencies

| Package | Extras |
| --- | --- |
| imageio-ffmpeg | `file-info-builder-audio`<br>`file-info-builder-video` |
| Pillow | `file-info-builder-image`<br>`file-info-builder-pdf`<br>`file-info-builder-video` |
| pypdf | `file-info-builder-pdf` |
| pypdfium2 | `file-info-builder-pdf` |
| soundfile | `file-info-builder-audio` |

`all` Extra は、上記の optional dependency をすべてインストールします。

## Installation

```bash
pip install "kiarina-agi-data-builder[all]"
```

## Features

### Capability-aware PDF fallback

PDF analysis bundle は、chat model の capabilities に応じて content を選択します。

| Capabilities | Content |
| --- | --- |
| Text only | PDFから抽出したテキスト |
| Image | ページ番号付きページ画像とPDFから抽出したテキスト |
| PDF | 元PDFまたは選択したページsegment |

PDF file specification の `analysis_dpi` で、fallbackページ画像の解像度を指定できます。

```python
from kiarina.agi.file_info_builder_impl.pdf import create_pdf_file_info_builder
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def build_pdf_info():
    file_blob = await read_file("/path/to/document.pdf")
    assert file_blob is not None
    builder = create_pdf_file_info_builder(analysis_enabled=True)
    return await builder.build(
        {
            "uri_or_file_path": file_blob.file_path,
            "analysis_dpi": 144,
        },
        file_blob,
        run_context=RunContext(),
    )
```

### Capability-aware video fallback

Video analysis bundle は、chat model の capabilities に応じて content を選択します。

| Capabilities | Content |
| --- | --- |
| Text only | 音声の transcript と ambient analysis |
| Image | Timestamp 付き video frame、transcript、ambient analysis |
| Video | 音声トラックを含む video |

Video file specification の `analysis_fps` で、準備する video と fallback image の frame rate を指定できます。

```python
from kiarina.agi.file_info_builder_impl.video import (
    create_video_file_info_builder,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file


async def build_video_info():
    file_blob = await read_file("/path/to/video.mp4")
    assert file_blob is not None
    builder = create_video_file_info_builder(
        analysis_enabled=True,
        audio_consumers=["stt", "ambient"],
    )
    return await builder.build(
        {
            "uri_or_file_path": file_blob.file_path,
            "analysis_fps": 1.0,
        },
        file_blob,
        run_context=RunContext(),
    )
```

## API Reference

### `kiarina.agi.file_info_builder_impl.pdf`

```python
from kiarina.agi.file_info_builder_impl.pdf import (
    PDFFileInfoBuilder,
    PDFFileInfoBuilderSettings,
    create_pdf_file_info_builder,
    settings_manager,
)
```

#### `create_pdf_file_info_builder`

```python
def create_pdf_file_info_builder(**kwargs: Any) -> PDFFileInfoBuilder: ...
```

管理された settings と任意の override から PDF file info builder を作成します。

#### `PDFFileInfoBuilder`

```python
class PDFFileInfoBuilder(BaseFileInfoBuilder):
    def __init__(self, settings: PDFFileInfoBuilderSettings) -> None: ...

    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult: ...
```

#### `PDFFileInfoBuilderSettings`

```python
class PDFFileInfoBuilderSettings(BaseSettings):
    analysis_enabled: bool = False
```

`settings_manager` は、factory が使用する `SettingsManager[PDFFileInfoBuilderSettings]` instance です。

### `kiarina.agi.file_info_builder_impl.video`

```python
from kiarina.agi.file_info_builder_impl.video import (
    VideoFileInfoBuilder,
    VideoFileInfoBuilderSettings,
    create_video_file_info_builder,
    settings_manager,
)
```

#### `create_video_file_info_builder`

```python
def create_video_file_info_builder(**kwargs: Any) -> VideoFileInfoBuilder: ...
```

管理された settings と任意の override から video file info builder を作成します。

#### `VideoFileInfoBuilder`

```python
class VideoFileInfoBuilder(BaseFileInfoBuilder):
    def __init__(self, settings: VideoFileInfoBuilderSettings) -> None: ...

    async def build(
        self,
        file_info_spec: FileInfoSpec,
        file_blob: FileBlob,
        *,
        run_context: RunContext,
    ) -> BuildResult: ...
```

#### `VideoFileInfoBuilderSettings`

```python
class VideoFileInfoBuilderSettings(BaseSettings):
    analysis_enabled: bool = False
    audio_source: AudioSourceSpecifier = "file?sample_rate=16000&start_timestamp=0.0"
    audio_consumers: list[AudioConsumerSpecifier] = [
        "stt?diarization_enabled=true",
        "ambient?window_seconds=10.0&top_k=3",
    ]
    audio_event_bundlers: list[AudioEventBundlerSpecifier] = ["stt", "ambient"]
```

`settings_manager` は、factory が使用する `SettingsManager[VideoFileInfoBuilderSettings]` instance です。
