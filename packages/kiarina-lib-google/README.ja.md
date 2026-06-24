# kiarina-lib-google

[English](README.md) | 日本語

kiarina namespace 向けの Google Cloud authentication / credentials library です。

## Features

- Application Default Credentials (ADC)
- service account file / JSON data
- authorized user credentials
- service account impersonation
- credentials cache
- self-signed JWT generation

## Installation

```bash
pip install kiarina-lib-google
```

## Quick Start

### Default Credentials (ADC)

```python
from kiarina.lib.google import get_credentials

credentials = get_credentials()
```

### Service Account

```python
from kiarina.lib.google import get_service_account_credentials

credentials = get_service_account_credentials(
    service_account_file="service-account.json",
)
```

### User Account (OAuth2)

```python
from kiarina.lib.google import get_user_account_credentials

credentials = get_user_account_credentials(
    authorized_user_file="authorized-user.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
```

### Service Account Impersonation

設定で impersonation target を指定すると、service account impersonation を利用できます。

### Credentials Caching

user account credentials の refresh result を cache 実装に保存できます。

### Self-Signed JWT

```python
from kiarina.lib.google import get_self_signed_jwt

jwt = get_self_signed_jwt(audience="https://example.googleapis.com/")
```

## Configuration

### YAML Configuration (Recommended)

```yaml
kiarina.lib.google:
  auth_type: "service_account"
  service_account_file: "service-account.json"
  scopes:
    - "https://www.googleapis.com/auth/cloud-platform"
```

### Environment Variables

`KIARINA_LIB_GOOGLE_` prefix の環境変数で設定できます。

### Programmatic Configuration

`GoogleSettings` を直接作成するか、`settings_manager.user_config` に dictionary を渡して設定します。

## API Reference

### Main Functions

#### `get_credentials(settings_key=None, *, settings=None, scopes=None, cache=None)`

設定に応じて Google credentials を取得します。

#### `get_self_signed_jwt(settings_key=None, *, settings=None, audience)`

service account credentials から self-signed JWT を生成します。

### Utility Functions

#### `get_default_credentials()`

Application Default Credentials を取得します。

#### `get_service_account_credentials(*, service_account_file=None, service_account_data=None)`

service account credentials を取得します。

#### `get_user_account_credentials(*, authorized_user_file=None, authorized_user_data=None, scopes, cache=None)`

authorized user credentials を取得します。

### Configuration

#### `GoogleSettings`

Google authentication 設定用の settings model です。

#### `CredentialsCache` (Protocol)

credentials cache 実装のための protocol です。

## Authentication Priority

### Default Credentials

明示的な認証設定がない場合は ADC を利用します。

### Default Scopes

必要に応じて default scopes を settings または関数引数で指定できます。

## Testing

### Setup Test Configuration

sample configuration をコピーし、認証情報を設定して環境変数を指定します。

### Run Tests

```bash
mise run package:check kiarina-lib-google
mise run package:test kiarina-lib-google --coverage
```

## Dependencies

- `google-api-python-client`
- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)

