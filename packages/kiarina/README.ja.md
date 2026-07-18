# kiarina

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/kiarina.svg)](https://badge.fury.io/py/kiarina)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kiarina/kiarina-python/blob/main/LICENSE)

[English](README.md) | 日本語

> [!NOTE] これは何？
> `kiarina` namespace のパッケージをまとめてインストールするためのメタパッケージです。

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-audio](https://pypi.org/project/kiarina-agi-audio/) | `>=2.15.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-base](https://pypi.org/project/kiarina-agi-base/) | `>=2.7.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-data](https://pypi.org/project/kiarina-agi-data/) | `>=2.7.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-data-builder](https://pypi.org/project/kiarina-agi-data-builder/) | `>=2.15.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-file](https://pypi.org/project/kiarina-agi-file/) | `>=2.8.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-flow](https://pypi.org/project/kiarina-agi-flow/) | `>=2.11.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-image](https://pypi.org/project/kiarina-agi-image/) | `>=2.15.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-runner](https://pypi.org/project/kiarina-agi-runner/) | `>=2.14.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-text](https://pypi.org/project/kiarina-agi-text/) | `>=2.8.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-tool](https://pypi.org/project/kiarina-agi-tool/) | `>=2.12.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-agi-video](https://pypi.org/project/kiarina-agi-video/) | `>=2.15.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-currency](https://pypi.org/project/kiarina-currency/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-i18n](https://pypi.org/project/kiarina-i18n/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-anthropic](https://pypi.org/project/kiarina-lib-anthropic/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-cloudflare](https://pypi.org/project/kiarina-lib-cloudflare/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-cloudflare-d1](https://pypi.org/project/kiarina-lib-cloudflare-d1/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-falkordb](https://pypi.org/project/kiarina-lib-falkordb/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-firebase](https://pypi.org/project/kiarina-lib-firebase/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-firebase-rtdb](https://pypi.org/project/kiarina-lib-firebase-rtdb/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-google](https://pypi.org/project/kiarina-lib-google/) | `>=2.8.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-openai](https://pypi.org/project/kiarina-lib-openai/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-redis](https://pypi.org/project/kiarina-lib-redis/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-redisearch](https://pypi.org/project/kiarina-lib-redisearch/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-lib-slack](https://pypi.org/project/kiarina-lib-slack/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-utils-app](https://pypi.org/project/kiarina-utils-app/) | `>=2.4.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-utils-common](https://pypi.org/project/kiarina-utils-common/) | `>=2.8.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [kiarina-utils-file](https://pypi.org/project/kiarina-utils-file/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |

### Optional Dependencies

`all` Extra は、下記のパッケージをそれぞれの `all` Extra 付きでインストールします。

- [kiarina-agi-audio](https://pypi.org/project/kiarina-agi-audio/)
- [kiarina-agi-data-builder](https://pypi.org/project/kiarina-agi-data-builder/)
- [kiarina-agi-file](https://pypi.org/project/kiarina-agi-file/)
- [kiarina-agi-image](https://pypi.org/project/kiarina-agi-image/)
- [kiarina-agi-text](https://pypi.org/project/kiarina-agi-text/)
- [kiarina-agi-video](https://pypi.org/project/kiarina-agi-video/)

## Installation

```bash
pip install kiarina
```

全ての optional dependency もインストールする場合:

```bash
pip install "kiarina[all]"
```
