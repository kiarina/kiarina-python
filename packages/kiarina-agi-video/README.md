# kiarina-agi-video

English | [日本語](README.ja.md)

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-video.svg)](https://pypi.org/project/kiarina-agi-video/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-video` provides video sources and video generation for AI agents.

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-image](../kiarina-agi-image/) | `>=2.9.0` | MIT |
| [kiarina-utils-app](../kiarina-utils-app/) | `>=2.4.0` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.8.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0,<3` | BSD-3-Clause |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7,<3` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1,<3` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |

### Optional Dependencies

| Package | Extras |
| --- | --- |
| google-genai | `video-generation-provider-google` |
| httpx | `video-generation-provider-kiapi` |
| kiarina-lib-google | `video-generation-provider-google` |
| imageio-ffmpeg | `video-source-file` |
| opencv-python | `video-source-camera` |

The `all` Extra installs every optional dependency listed above.

## Video Generation through kiapi

The `kiapi` model alias uses kiapi at `http://localhost:8000` and the `ltx2` family by default. Pass family-specific request parameters in `extra_params`.

```python
from kiarina.agi.video_generation_model import create_video

session_id = await create_video(
    "A cat walking through tall grass",
    video_generation_options={
        "video_generation_model": "kiapi?family=ltx2&extra_params.width=512&extra_params.num_frames=97"
    },
    run_context=run_context,
)
```

When `first_image_file_path` is supplied, the file is uploaded to kiapi and used as first-frame conditioning. Generation starts as an asynchronous job that can be managed with the existing `is_video_running`, `get_video`, and `delete_video` helpers.

## Public API

### `kiarina.agi.video_generation_provider_impl.kiapi`

```python
from kiarina.agi.video_generation_provider_impl.kiapi import (
    KiapiVideoGenerationProvider,
    KiapiVideoGenerationProviderSettings,
    create_kiapi_video_generation_provider,
    settings_manager,
)
```

#### `create_kiapi_video_generation_provider`

```python
def create_kiapi_video_generation_provider(
    **kwargs: Any,
) -> KiapiVideoGenerationProvider: ...
```

Creates a provider from managed settings, with keyword arguments applied as overrides.

#### `KiapiVideoGenerationProvider`

```python
class KiapiVideoGenerationProvider(BaseVideoGenerationProvider):
    def __init__(self, settings: KiapiVideoGenerationProviderSettings) -> None: ...
```

Generates, retrieves, and deletes videos through the kiapi asynchronous job API. kiapi does not currently support video editing or extension.

#### `KiapiVideoGenerationProviderSettings`

```python
class KiapiVideoGenerationProviderSettings(BaseSettings):
    kiapi_base_url: str = "http://localhost:8000"
    family: Literal["ltx2"] = "ltx2"
    timeout: float = 1800.0
    extra_params: dict[str, Any] = {}
```

`settings_manager` is the `SettingsManager` instance for these settings.
