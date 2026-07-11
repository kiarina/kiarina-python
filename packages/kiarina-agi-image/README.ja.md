# kiarina-agi-image

[English](README.md) | 日本語

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-image.svg)](https://pypi.org/project/kiarina-agi-image/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-image` は、AI agent 向けの image detection、embedding、generation を提供します。

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-data](../kiarina-agi-data/) | `>=2.7.0` | MIT |
| [kiarina-agi-file](../kiarina-agi-file/) | `>=2.6.0` | MIT |
| [kiarina-utils-app](../kiarina-utils-app/) | `>=2.4.0` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.3.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0,<3` | BSD-3-Clause |
| [OpenCV](https://github.com/opencv/opencv-python) | `>=4.12.0,<5` | Apache-2.0 |
| [Pillow](https://github.com/python-pillow/Pillow) | `>=11.3.0,<12` | HPND |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7,<3` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1,<3` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |

### Optional Dependencies

| Package | Extras |
| --- | --- |
| google-genai | `image-embedding-provider-gemini`<br>`image-generation-provider-google` |
| httpx | `image-embedding-provider-qwen3-vl`<br>`image-generation-provider-kiapi`<br>`image-generation-provider-openai` |
| kiarina-lib-google | `image-embedding-provider-gemini`<br>`image-generation-provider-google` |
| kiarina-lib-openai | `image-generation-provider-openai` |
| onnxruntime | `image-detection-provider-dfine`<br>`image-embedding-provider-siglip2` |
| openai | `image-generation-provider-openai` |

`all` Extra は、上記の optional dependency をすべてインストールします。

## Installation

```bash
pip install kiarina-agi-image
```

すべての provider implementation を利用する場合:

```bash
pip install "kiarina-agi-image[all]"
```

## Features

- **Image Detection**
  Object と face を検出し、crop や face alignment を行います。
- **Image Embedding**
  Image embedding を生成します。
- **Image Generation**
  Google、OpenAI、kiapi、mock provider で画像を生成・編集します。

### Image Generation through kiapi

`kiapi` model alias は、既定で `http://localhost:8000` の kiapi と `qwen` family を使用します。`family` は `flux2`、`qwen`、`ernie` から選択でき、family 固有の request parameter は `extra_params` に指定します。

```python
from kiarina.agi.image_generation_model import generate_image

result = await generate_image(
    "A cafe sign that reads KIARINA",
    image_generation_options={
        "image_generation_model": "kiapi?family=flux2&extra_params.width=512&extra_params.height=512"
    },
)
```

`file_paths` を指定すると、file を kiapi に upload し、選択した family の edit endpoint に渡します。`ernie` は入力画像を 1 枚だけ受け取ります。

### Model Cache

YuNet、D-FINE、SFace、SigLIP2 は、`model_path` が `None` の場合、初回利用時に既定モデルをダウンロードします。D-FINE は、`label_map_path` が `None` の場合、検証済みの `config.json` をダウンロードし、そこから既定ラベルを生成します。

ファイルは `user_directory.get_user_cache_dir() / "models" / <implementation>` にキャッシュされます。明示したパスは常に優先され、その場合は対応するファイルをダウンロードしません。

既定の download URL、SHA-256 digest、cache filename は provider settings であり、settings、環境変数、config で上書きできます。取得元を変える場合、既存 cache を再利用したくないときは filename も変更してください。

## API Reference

### `kiarina.agi.image_detection_model`

Image detection model の設定、registry、検出・crop helper を公開します。

### `kiarina.agi.image_detection_provider`

Image detection provider protocol、base class、検出結果 view、registry を公開します。

### `kiarina.agi.image_embedding_model`

Image embedding model の設定、registry、embedding helper を公開します。

### `kiarina.agi.image_embedding_provider`

Image embedding provider protocol、base class、registry を公開します。

### `kiarina.agi.image_generation_model`

Image generation model の設定、registry、generation helper を公開します。

### `kiarina.agi.image_generation_provider`

Image generation provider protocol、base class、result view、registry を公開します。

Provider implementation は、対応する `kiarina.agi.*_provider_impl.<name>` から import します。

### `kiarina.agi.image_generation_provider_impl.kiapi`

```python
from kiarina.agi.image_generation_provider_impl.kiapi import (
    KiapiImageGenerationProvider,
    KiapiImageGenerationProviderSettings,
    create_kiapi_image_generation_provider,
    settings_manager,
)
```

#### `create_kiapi_image_generation_provider`

```python
def create_kiapi_image_generation_provider(
    **kwargs: Any,
) -> KiapiImageGenerationProvider: ...
```

管理された settings から provider を作成し、keyword argument を上書きとして適用します。

#### `KiapiImageGenerationProvider`

```python
class KiapiImageGenerationProvider(BaseImageGenerationProvider):
    def __init__(self, settings: KiapiImageGenerationProviderSettings) -> None: ...
```

kiapi の `flux2`、`qwen`、`ernie` family で画像を生成・編集します。

#### `KiapiImageGenerationProviderSettings`

```python
class KiapiImageGenerationProviderSettings(BaseSettings):
    kiapi_base_url: str = "http://localhost:8000"
    family: Literal["flux2", "qwen", "ernie"] = "qwen"
    timeout: float = 1800.0
    extra_params: dict[str, Any] = {}
```

`settings_manager` は、この settings 用の `SettingsManager` instance です。
