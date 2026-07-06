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
| httpx | `image-embedding-provider-qwen3-vl`<br>`image-generation-provider-openai` |
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
  Generate and edit images with Google, OpenAI, and mock providers.

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
