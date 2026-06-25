# kiarina-lib-google

[English](README.md) | 日本語

pydantic-settings-manager による設定管理に対応した、Google Cloud 認証用の Python ライブラリです。

## Features

- **複数の認証方式**: デフォルト認証情報（ADC）、サービスアカウント、ユーザーアカウント
- **サービスアカウントの権限借用**: 設定可能なスコープによる委任アクセス
- **設定管理**: pydantic-settings-manager による柔軟な設定
- **認証情報のキャッシュ**: ユーザーアカウントの認証情報を自動的にキャッシュおよび更新
- **自己署名 JWT**: サービスアカウント認証用の JWT を生成
- **型安全性**: 完全な型ヒントと Pydantic による検証

## Installation

```bash
pip install kiarina-lib-google
```

## Quick Start

### Default Credentials (ADC)

```python
from kiarina.lib.google import get_credentials

# Application Default Credentials を使用
credentials = get_credentials()
```

### Service Account

```python
from kiarina.lib.google import get_credentials, GoogleSettings

# キーファイルから読み込み
credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_file="~/path/to/key.json"
    )
)

# JSON データから読み込み
credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_data='{"type":"service_account",...}'
    )
)
```

### User Account (OAuth2)

```python
# 認証済みユーザーファイルから読み込み
credentials = get_credentials(
    settings=GoogleSettings(
        type="user_account",
        authorized_user_file="~/.config/gcloud/application_default_credentials.json",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
)
```

### Service Account Impersonation

```python
# サービスアカウントの権限を借用
credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_file="~/source-key.json",
        impersonate_service_account="target@project.iam.gserviceaccount.com",
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
)
```

**注記**: 呼び出し元のプリンシパルには `roles/iam.serviceAccountTokenCreator` ロールが必要です。

### Credentials Caching

```python
from kiarina.lib.google import CredentialsCache

class InMemoryCache(CredentialsCache):
    def __init__(self):
        self._cache: str | None = None

    def get(self) -> str | None:
        return self._cache

    def set(self, value: str) -> None:
        self._cache = value

# ユーザーアカウントの認証情報にキャッシュを使用
credentials = get_credentials(
    settings=GoogleSettings(
        type="user_account",
        authorized_user_file="~/authorized-user.json",
        scopes=["https://www.googleapis.com/auth/drive"]
    ),
    cache=InMemoryCache()
)
```

### Self-Signed JWT

```python
from kiarina.lib.google import get_self_signed_jwt

jwt_token = get_self_signed_jwt(
    settings=GoogleSettings(
        type="service_account",
        service_account_file="~/key.json"
    ),
    audience="https://your-service.example.com/"
)
```

## Configuration

### YAML Configuration (Recommended)

```yaml
kiarina.lib.google:
  development:
    type: user_account
    authorized_user_file: ~/.config/gcloud/application_default_credentials.json
    scopes:
      - https://www.googleapis.com/auth/cloud-platform

  production:
    type: service_account
    service_account_file: /secrets/prod-sa-key.json
    project_id: your-project-id
    scopes:
      - https://www.googleapis.com/auth/cloud-platform

  impersonation:
    type: service_account
    service_account_file: ~/source-key.json
    impersonate_service_account: target@project.iam.gserviceaccount.com
    scopes:
      - https://www.googleapis.com/auth/cloud-platform
```

設定を読み込みます。

```python
from pydantic_settings_manager import load_user_configs
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)
    load_user_configs(config)

# 設定済みの認証情報を使用
from kiarina.lib.google import get_credentials
credentials = get_credentials("production")
```

### Environment Variables

```bash
export KIARINA_LIB_GOOGLE_TYPE="service_account"
export KIARINA_LIB_GOOGLE_SERVICE_ACCOUNT_FILE="~/key.json"
export KIARINA_LIB_GOOGLE_PROJECT_ID="your-project-id"
export KIARINA_LIB_GOOGLE_SCOPES="https://www.googleapis.com/auth/cloud-platform"
```

### Programmatic Configuration

```python
from kiarina.lib.google import settings_manager

settings_manager.user_config = {
    "dev": {
        "type": "user_account",
        "authorized_user_file": "~/.config/gcloud/application_default_credentials.json"
    },
    "prod": {
        "type": "service_account",
        "service_account_file": "/secrets/key.json"
    }
}

settings_manager.active_key = "prod"
credentials = get_credentials()
```

## API Reference

### Main Functions

#### `get_credentials(settings_key=None, *, settings=None, scopes=None, cache=None)`

設定に基づいて Google Cloud の認証情報を取得します。

**引数:**
- `settings_key` (str | None): 複数設定を使用する場合の設定キー
- `settings` (GoogleSettings | None): 設定オブジェクト（settings_key より優先）
- `scopes` (list[str] | None): OAuth2 スコープ（settings.scopes より優先）
- `cache` (CredentialsCache | None): ユーザーアカウント用の認証情報キャッシュ

**戻り値:** `Credentials` - Google Cloud の認証情報

#### `get_self_signed_jwt(settings_key=None, *, settings=None, audience)`

サービスアカウント認証用の自己署名 JWT を生成します。

**引数:**
- `settings_key` (str | None): 設定キー
- `settings` (GoogleSettings | None): 設定オブジェクト
- `audience` (str): JWT の対象（対象サービスの URL）

**戻り値:** `str` - 自己署名 JWT トークン

### Utility Functions

#### `get_default_credentials()`

Application Default Credentials（ADC）を使用してデフォルトの認証情報を取得します。

**戻り値:** `Credentials`

#### `get_service_account_credentials(*, service_account_file=None, service_account_data=None)`

ファイルまたはデータからサービスアカウントの認証情報を取得します。

**戻り値:** `google.oauth2.service_account.Credentials`

#### `get_user_account_credentials(*, authorized_user_file=None, authorized_user_data=None, scopes=None, cache=None)`

任意のキャッシュを使用して、ファイルまたはデータからユーザーアカウントの認証情報を取得します。

**戻り値:** `google.oauth2.credentials.Credentials`

### Configuration

#### `GoogleSettings`

認証設定用の Pydantic settings モデルです。

**主なフィールド:**
- `type`: 認証方式（`"default"`、`"service_account"`、`"user_account"`）
- `service_account_file`: サービスアカウントのキーファイルへのパス
- `service_account_data`: サービスアカウントのキーデータ（JSON 文字列、SecretStr）
- `authorized_user_file`: 認証済みユーザーファイルへのパス
- `authorized_user_data`: 認証済みユーザーデータ（JSON 文字列、SecretStr）
- `impersonate_service_account`: 権限借用の対象となるサービスアカウントのメールアドレス
- `scopes`: OAuth2 スコープ（デフォルト: 空）
- `project_id`: GCP プロジェクト ID

**ヘルパーメソッド:**
- `get_service_account_data()`: service_account_data の JSON を解析
- `get_client_secret_data()`: client_secret_data の JSON を解析
- `get_authorized_user_data()`: authorized_user_data の JSON を解析

#### `CredentialsCache` (Protocol)

認証情報キャッシュを実装するためのプロトコルです。

**メソッド:**
- `get() -> str | None`: キャッシュされた認証情報（JSON 文字列）を取得
- `set(value: str) -> None`: 認証情報（JSON 文字列）を保存

## Authentication Priority

### Default Credentials

Application Default Credentials（ADC）は次の順序で使用されます。

1. `GOOGLE_APPLICATION_CREDENTIALS` 環境変数（サービスアカウント）
2. `gcloud auth application-default login` の認証情報（ユーザーアカウント）
3. Compute Engine メタデータサーバー（Compute Engine）

### Default Scopes

デフォルトではスコープを要求しません。設定または関数呼び出しで、アプリケーションに
必要なスコープのみを指定してください。

スコープが指定されていない場合、ユーザーアカウントの認証情報では、認証済みユーザー
データに保存されたスコープを再利用します。サービスアカウントの権限借用には、少なくとも
1 つのスコープを明示的に指定する必要があります。

## Testing

### Setup Test Configuration

> [!Note] ADC のテスト
> デフォルト認証情報（ADC）を使用するテストには、Google Cloud への認証が必要です。テストを実行する前に `gcloud auth application-default login` を実行してください。

```bash
# サンプル設定をコピー
cp packages/kiarina-lib-google/test_settings.sample.yaml \
   packages/kiarina-lib-google/test_settings.yaml

# 認証情報を設定
# 環境変数を設定
export KIARINA_LIB_GOOGLE_TEST_SETTINGS_FILE="packages/kiarina-lib-google/test_settings.yaml"
```

### Run Tests

```bash
# すべてのチェックを実行
mise run package:check kiarina-lib-google

# カバレッジを取得してテストを実行
mise run package:test kiarina-lib-google --coverage
```

## Dependencies

- [google-api-python-client](https://github.com/googleapis/google-api-python-client) - Google API クライアント
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - 設定管理
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - 高度な設定管理

## License

MIT License です。詳細は [LICENSE](../../LICENSE) ファイルを参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - メインのモノレポ
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - 設定管理ライブラリ
