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
| imageio-ffmpeg | `file-info-builder-audio` |
| MoviePy | `file-info-builder-video` |
| Pillow | `file-info-builder-image` |
| pypdf | `file-info-builder-pdf` |
| soundfile | `file-info-builder-audio` |

`all` Extra は、上記の optional dependency をすべてインストールします。
