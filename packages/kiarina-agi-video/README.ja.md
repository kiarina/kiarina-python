# kiarina-agi-video

[English](README.md) | 日本語

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-video.svg)](https://pypi.org/project/kiarina-agi-video/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] これは何？
> `kiarina-agi-video` は、AI agent 向けの video source と video generation を提供します。

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

`all` Extra は、上記の optional dependency をすべてインストールします。

## Video Generation through kiapi

`kiapi` model alias は、既定で `http://localhost:8000` の kiapi と `ltx2` family を使用します。family 固有の request parameter は `extra_params` に指定します。

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

`first_image_file_path` を指定すると、file を kiapi に upload し、先頭 frame の条件画像として使用します。生成は非同期 job として開始され、既存の `is_video_running`、`get_video`、`delete_video` helper で管理できます。

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

管理された settings から provider を作成し、keyword argument を上書きとして適用します。

#### `KiapiVideoGenerationProvider`

```python
class KiapiVideoGenerationProvider(BaseVideoGenerationProvider):
    def __init__(self, settings: KiapiVideoGenerationProviderSettings) -> None: ...
```

kiapi の非同期 job API を使用して動画を生成、取得、削除します。kiapi は現在、動画の編集と延長には対応していません。

#### `KiapiVideoGenerationProviderSettings`

```python
class KiapiVideoGenerationProviderSettings(BaseSettings):
    kiapi_base_url: str = "http://localhost:8000"
    family: Literal["ltx2"] = "ltx2"
    timeout: float = 1800.0
    extra_params: dict[str, Any] = {}
```

`settings_manager` は、この settings 用の `SettingsManager` instance です。
