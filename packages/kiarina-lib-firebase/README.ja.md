# kiarina-lib-firebase

[English](README.md) | [日本語](README.ja.md)

kiarina namespace 向けの Firebase authentication library です。

## Purpose

Firebase REST API を使った custom token exchange、ID token refresh、automatic token lifecycle management を提供します。

## Installation

```bash
pip install kiarina-lib-firebase
```

## Quick Start

### Basic Usage

```python
from kiarina.lib.firebase import TokenManager, exchange_custom_token, settings_manager

settings_manager.user_config = {
    "default": {
        "api_key": "your-firebase-api-key",
    },
}

settings = settings_manager.settings
token_data = await exchange_custom_token("custom-token", settings.api_key.get_secret_value())

token_manager = TokenManager(
    api_key=settings.api_key.get_secret_value(),
    token_data=token_data,
)
id_token = await token_manager.get_id_token()
```

### Manual Token Refresh

```python
from kiarina.lib.firebase import refresh_id_token

token_data = await refresh_id_token("refresh-token", "firebase-api-key")
```

## API Reference

### Settings

#### `FirebaseSettings`

Firebase API key を保持する settings model です。API key は `SecretStr` で保護されます。

### Functions

#### `exchange_custom_token(custom_token: str, api_key: str) -> TokenData`

custom token を ID token / refresh token に交換します。

#### `refresh_id_token(refresh_token: str, api_key: str) -> TokenData`

refresh token を使って ID token を更新します。

### Classes

#### `TokenManager`

ID token の期限を管理し、期限切れ前に自動 refresh します。`token_data`、`refresh_token`、または `token_data_cache` を使って初期化できます。

#### `TokenData`

refresh token、ID token、expiration time を保持する schema です。

#### `TokenDataCache`

persistent token storage 実装のための protocol です。

### Exceptions

#### `FirebaseAuthError`

Firebase authentication 関連 error の base exception です。

#### `InvalidCustomTokenError`

custom token が無効な場合に送出されます。

#### `InvalidRefreshTokenError`

refresh token が無効な場合に送出されます。

#### `FirebaseAPIError`

Firebase API response が error の場合に送出されます。

## Configuration

### YAML Configuration

```yaml
kiarina.lib.firebase:
  api_key: "your-firebase-api-key"
```

### Environment Variables

```bash
export KIARINA_LIB_FIREBASE_API_KEY="your-firebase-api-key"
```

### Multi-Configuration Support

```python
from kiarina.lib.firebase import settings_manager

settings_manager.user_config = {
    "dev": {"api_key": "dev-api-key"},
    "prod": {"api_key": "prod-api-key"},
}
settings_manager.active_key = "prod"
```

## Testing

### Setup

Firebase Admin SDK を使う統合テストでは、test settings と認証情報を用意します。

## Dependencies

- `httpx`
- `pydantic`
- `pydantic-settings`
- `pydantic-settings-manager`

### Development Dependencies

- `firebase-admin`
- `kiarina-lib-google`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Firebase Authentication](https://firebase.google.com/docs/auth)

