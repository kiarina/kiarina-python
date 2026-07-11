# kiarina-agi-image

English | [日本語](README.ja.md)

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-image.svg)](https://pypi.org/project/kiarina-agi-image/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-image` provides image detection, embedding, and generation for AI agents.

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

The `all` Extra installs every optional dependency listed above.

## Installation

```bash
pip install kiarina-agi-image
```

To use every provider implementation:

```bash
pip install "kiarina-agi-image[all]"
```

## Features

- **Image Detection**
  Detect objects and faces, crop objects, and align faces.
- **Image Embedding**
  Create image embeddings.
- **Image Generation**
  Generate and edit images with Google, OpenAI, kiapi, and mock providers.

### Image Generation through kiapi

The `kiapi` model alias uses kiapi at `http://localhost:8000` and the `qwen` family by default. Select `flux2`, `qwen`, or `ernie` with `family`, and pass family-specific request parameters in `extra_params`.

```python
from kiarina.agi.image_generation_model import generate_image

result = await generate_image(
    "A cafe sign that reads KIARINA",
    image_generation_options={
        "image_generation_model": "kiapi?family=flux2&extra_params.width=512&extra_params.height=512"
    },
)
```

When `file_paths` are supplied, the files are uploaded to kiapi and passed to the selected family's edit endpoint. The `ernie` family accepts one input image.

### Model Cache

YuNet, D-FINE, SFace, and SigLIP2 download their default model on first use when `model_path` is `None`. D-FINE also downloads a verified `config.json` and generates default labels from it when `label_map_path` is `None`.

Files are cached under `user_directory.get_user_cache_dir() / "models" / <implementation>`. An explicit path always takes precedence and prevents downloading the corresponding file.

The default download URL, SHA-256 digest, and cache filename are provider settings and can be overridden through settings, environment variables, or config. When changing the source, also change the filename if an existing cached file should not be reused.

## API Reference

### `kiarina.agi.image_detection_model`

Exports image detection model settings, registries, detection helpers, and cropping helpers.

### `kiarina.agi.image_detection_provider`

Exports the image detection provider protocol, base class, detection result view, and registry.

### `kiarina.agi.image_embedding_model`

Exports image embedding model settings, registry, and embedding helper.

### `kiarina.agi.image_embedding_provider`

Exports the image embedding provider protocol, base class, and registry.

### `kiarina.agi.image_generation_model`

Exports image generation model settings, registry, and generation helper.

### `kiarina.agi.image_generation_provider`

Exports the image generation provider protocol, base class, result view, and registry.

Import provider implementations from the matching `kiarina.agi.*_provider_impl.<name>` path.

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

Creates a provider from managed settings, with keyword arguments applied as overrides.

#### `KiapiImageGenerationProvider`

```python
class KiapiImageGenerationProvider(BaseImageGenerationProvider):
    def __init__(self, settings: KiapiImageGenerationProviderSettings) -> None: ...
```

Generates and edits images with the kiapi `flux2`, `qwen`, and `ernie` families.

#### `KiapiImageGenerationProviderSettings`

```python
class KiapiImageGenerationProviderSettings(BaseSettings):
    kiapi_base_url: str = "http://localhost:8000"
    family: Literal["flux2", "qwen", "ernie"] = "qwen"
    timeout: float = 1800.0
    extra_params: dict[str, Any] = {}
```

`settings_manager` is the `SettingsManager` instance for these settings.
