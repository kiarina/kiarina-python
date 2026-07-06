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
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.3.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0,<3` | BSD-3-Clause |
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
| opencv-python | `image-detection-provider-dfine`<br>`image-detection-provider-yunet`<br>`image-embedding-provider-qwen3-vl`<br>`image-embedding-provider-sface`<br>`image-embedding-provider-siglip2` |

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
  Google、OpenAI、mock provider で画像を生成・編集します。

## API Reference

### `kiarina.agi.image_detection_model`

Image detection model の設定、registry、検出・crop helper を公開します。

### `kiarina.agi.image_detection_provider`

Image detection provider protocol、base class、検出結果 schema、registry を公開します。

### `kiarina.agi.image_embedding_model`

Image embedding model の設定、registry、embedding helper を公開します。

### `kiarina.agi.image_embedding_provider`

Image embedding provider protocol、base class、registry を公開します。

### `kiarina.agi.image_generation_model`

Image generation model の設定、registry、generation helper を公開します。

### `kiarina.agi.image_generation_provider`

Image generation provider protocol、base class、result schema、registry を公開します。

Provider implementation は、対応する `kiarina.agi.*_provider_impl.<name>` から import します。
