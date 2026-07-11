# kiarina-agi-audio

[English](README.md) | 日本語

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-audio.svg)](https://pypi.org/project/kiarina-agi-audio/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-audio` は、AI agent 向けの audio source、speech-to-text、text-to-speech、voice activity detection、speaker change detection、audio tagging、audio embedding を提供します。

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [jaxtyping](https://github.com/patrick-kidger/jaxtyping) | `>=0.3.3` | MIT |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-data](../kiarina-agi-data/) | `>=2.7.0` | MIT |
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
| ai-edge-litert | `audio-tagging-provider-yamnet` |
| google-genai | `asr-provider-google`<br>`tts-provider-google` |
| imageio-ffmpeg | `tts-provider-command`<br>`tts-provider-google`<br>`tts-provider-mock`<br>`tts-provider-openai` |
| kiarina-lib-google | `asr-provider-google`<br>`tts-provider-google` |
| kiarina-lib-openai | `asr-provider-openai`<br>`tts-provider-openai` |
| onnxruntime | `audio-embedding-provider-clap-onnx`<br>`audio-embedding-provider-ecapa-tdnn-onnx`<br>`scd-provider-pyannote`<br>`vad-provider-silero` |
| openai | `asr-provider-openai`<br>`tts-provider-openai` |
| sounddevice | `audio-source-mic` |
| soundfile | `audio-source-file` |
| tiktoken | `tts-provider-openai` |

`all` Extra は、上記の optional dependency をすべてインストールします。
