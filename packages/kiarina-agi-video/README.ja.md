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
| kiarina-lib-google | `video-generation-provider-google` |
| imageio-ffmpeg | `video-source-file` |
| opencv-python | `video-source-camera` |

`all` Extra は、上記の optional dependency をすべてインストールします。
