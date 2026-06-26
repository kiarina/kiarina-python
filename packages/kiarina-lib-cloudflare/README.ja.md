# kiarina-lib-cloudflare

[English](README.md) | 日本語

kiarina namespace 向けの Cloudflare client / authentication 設定 library です。

## Features

- **Configuration Management**: `pydantic-settings-manager` による設定管理
- **Type Safety**: type hints と Pydantic validation
- **Secure Credential Handling**: API token を `SecretStr` で保護
- **Multiple Configurations**: account ごとの複数設定
- **Environment Variable Support**: `KIARINA_LIB_CLOUDFLARE_` prefix の環境変数

## Installation

```bash
pip install kiarina-lib-cloudflare
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.cloudflare import settings_manager

settings_manager.user_config = {
    "default": {
        "account_id": "your-account-id",
        "api_token": "your-api-token",
    },
}

settings = settings_manager.settings
```

### Environment Variable Configuration

```bash
export KIARINA_LIB_CLOUDFLARE_ACCOUNT_ID="your-account-id"
export KIARINA_LIB_CLOUDFLARE_API_TOKEN="your-api-token"
```

### Multiple Configurations

```python
settings_manager.user_config = {
    "account_a": {"account_id": "account-a", "api_token": "token-a"},
    "account_b": {"account_id": "account-b", "api_token": "token-b"},
}
settings_manager.active_key = "account_a"
```

## Configuration

### CloudflareSettings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | `str` | Yes | Cloudflare Account ID |
| `api_token` | `SecretStr` | Yes | Cloudflare API token |

### Environment Variables

```bash
export KIARINA_LIB_CLOUDFLARE_ACCOUNT_ID="your-account-id"
export KIARINA_LIB_CLOUDFLARE_API_TOKEN="your-api-token"
```

### Programmatic Configuration

```python
from pydantic import SecretStr
from kiarina.lib.cloudflare import CloudflareSettings, settings_manager

settings = CloudflareSettings(
    account_id="your-account-id",
    api_token=SecretStr("your-api-token"),
)
settings_manager.user_config = {
    "default": {
        "account_id": "your-account-id",
        "api_token": "your-api-token",
    },
}
```

### Runtime Overrides

```python
settings_manager.cli_args = {"account_id": "override-account-id"}
```

## Security

### API Token Protection

API token は `SecretStr` で保持され、log や debug output に実値が出にくい形で扱われます。

## API Reference

### CloudflareSettings

Cloudflare 認証設定用の Pydantic settings model です。

### settings_manager

Cloudflare 設定用の global settings manager instance です。

## Development

### Prerequisites

Python 3.12+ が必要です。

### Setup

```bash
mise run setup
```

### Running Tests

```bash
cd packages/kiarina-lib-cloudflare && make check
mise run test kiarina-lib-cloudflare --coverage
```

## Dependencies

- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Contributing

issue や pull request は歓迎します。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager)

