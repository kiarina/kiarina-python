# kiarina-agi-data-builder

## What is this?

`kiarina-agi-data-builder` provides builders for AI agent messages, events, histories, tool info, file info, and file segments.

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

The `all` Extra installs every optional dependency listed above.

## Installation

```bash
pip install "kiarina-agi-data-builder[all]"
```

## Features

### Capability-aware PDF fallback

PDF analysis bundles select content from chat model capabilities.

| Capabilities | Content |
| --- | --- |
| Text only | Extracted PDF text |
| Image | Page-numbered page images and extracted PDF text |
| PDF | The original PDF or selected page segment |

Set `analysis_dpi` on the PDF file specification to control the resolution of fallback page images.

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

Video analysis bundles select content from chat model capabilities.

| Capabilities | Content |
| --- | --- |
| Text only | Audio transcript and ambient analysis |
| Image | Timestamped video frames, transcript, and ambient analysis |
| Video | Video with its audio track |

Set `analysis_fps` on the video file specification to control the frame rate of the prepared video and fallback images.

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

Creates a PDF file info builder from managed settings and optional overrides.

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

`settings_manager` is the `SettingsManager[PDFFileInfoBuilderSettings]` instance used by the factory.

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

Creates a video file info builder from managed settings and optional overrides.

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

`settings_manager` is the `SettingsManager[VideoFileInfoBuilderSettings]` instance used by the factory.
