# kiarina-lib-google

[![PyPI version](https://badge.fury.io/py/kiarina-lib-google.svg)](https://badge.fury.io/py/kiarina-lib-google)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-google.svg)](https://pypi.org/project/kiarina-lib-google/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] これは何？
> Google の認証情報を pydantic-settings-manager で管理・供給するためのパッケージ。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Google API Python Client](https://github.com/googleapis/google-api-python-client) | `>=2.184.0` | [Apache-2.0](https://github.com/googleapis/google-api-python-client/blob/main/LICENSE) |
| [Pydantic Settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-lib-google
```

## Features

- **Using Application Default Credentials**
  実行環境に設定された Application Default Credentials（ADC）を取得できます。
- **Authenticating with a Service Account**
  JSON キーファイルまたは JSON データからサービスアカウント認証情報を生成できます。
- **Authenticating with a User Account**
  認証済みユーザーデータを読み込み、期限切れの認証情報を更新・キャッシュできます。
- **Impersonating a Service Account**
  元の認証情報から、指定したサービスアカウントの短期認証情報を生成できます。
- **Managing Multiple Configurations**
  pydantic-settings-manager で複数の認証設定を一元管理できます。
- **Integrating Authentication into Service Implementations**
  Google 認証が必要な service の設定へ認証設定キーを注入し、client の生成時に認証情報を解決できます。
- **Configuring Google Gen AI Clients**
  `GoogleSettings` から `google.genai.Client` と `ChatGoogleGenerativeAI` の初期化 options を生成できます。
- **Generating a Self-Signed JWT**
  署名可能な認証情報から、対象サービス向けの自己署名 JWT を生成できます。

### Using Application Default Credentials

ADC は `GOOGLE_APPLICATION_CREDENTIALS`、ローカルの gcloud 認証情報、Google Cloud のメタデータサーバーなど、実行環境から利用可能な認証情報を探索します。

認証情報は、次の順序で探索されます。

1. `GOOGLE_APPLICATION_CREDENTIALS` が参照する認証情報ファイル
2. `gcloud auth application-default login` が作成したローカル認証情報ファイル
3. Google Cloud のメタデータサーバーが返す、実行環境に接続されたサービスアカウント

詳細は、Google Cloud の [Application Default Credentials の仕組み](https://cloud.google.com/docs/authentication/application-default-credentials?hl=ja) を参照してください。

```python
from kiarina.lib.google import get_credentials

credentials = get_credentials()
```

### Authenticating with a Service Account

サービスアカウントの JSON キーファイルを使用します。

```python
from kiarina.lib.google import GoogleSettings, get_credentials

credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_file="~/path/to/key.json",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
)
```

JSON 文字列を設定へ直接渡すこともできます。`service_account_data` は `SecretStr` として保持され、通常の文字列表現には秘密値が表示されません。

```python
credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_data='{"type":"service_account","project_id":"example",...}',
    )
)
```

### Authenticating with a User Account

ユーザーアカウントでは、認証済みユーザーファイルまたは JSON データを使用できます。`scopes` を省略すると、認証済みユーザーデータに保存されたスコープを再利用します。

```python
credentials = get_credentials(
    settings=GoogleSettings(
        type="user_account",
        authorized_user_file=(
            "~/.config/gcloud/application_default_credentials.json"
        ),
        scopes=["https://www.googleapis.com/auth/drive"],
    )
)
```

`CredentialsCache` を実装すると、有効な認証情報または更新された認証情報を JSON 文字列として保存し、次回の解決で再利用できます。

```python
from kiarina.lib.google import CredentialsCache


class InMemoryCache(CredentialsCache):
    def __init__(self) -> None:
        self._value: str | None = None

    def get(self) -> str | None:
        return self._value

    def set(self, value: str) -> None:
        self._value = value


credentials = get_credentials(
    settings=GoogleSettings(
        type="user_account",
        authorized_user_file="~/authorized-user.json",
    ),
    cache=InMemoryCache(),
)
```

### Impersonating a Service Account

`impersonate_service_account` を設定すると、解決した認証情報を source credentials としてサービスアカウントの権限を借用します。権限借用では 1 つ以上のスコープが必須です。

```python
credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_file="~/source-key.json",
        impersonate_service_account="target@project.iam.gserviceaccount.com",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
)
```

呼び出し元の principal には、対象サービスアカウントに対する `roles/iam.serviceAccountTokenCreator` ロールが必要です。

### Managing Multiple Configurations

`settings_manager` は複数設定モードで構成されています。pydantic-settings-manager v3 の structured format では、名前付き設定を `configs` に配置します。

```yaml
kiarina.lib.google:
  default: production
  configs:
    development:
      type: user_account
      authorized_user_file: ~/.config/gcloud/application_default_credentials.json
      scopes:
        - https://www.googleapis.com/auth/cloud-platform
    production:
      type: service_account
      service_account_file: /secrets/production-service-account.json
      scopes:
        - https://www.googleapis.com/auth/cloud-platform
```

アプリケーションの bootstrap 処理で設定を読み込み、設定名を `get_credentials` に渡します。

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.google import get_credentials

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

credentials = get_credentials("production")
```

このパッケージだけを直接設定する場合は、`settings_manager.user_config` へ structured format を設定できます。

```python
from kiarina.lib.google import get_credentials, settings_manager

settings_manager.user_config = {
    "default": "production",
    "configs": {
        "development": {
            "type": "user_account",
            "authorized_user_file": (
                "~/.config/gcloud/application_default_credentials.json"
            ),
        },
        "production": {
            "type": "service_account",
            "service_account_file": "/secrets/service-account.json",
        },
    },
}

credentials = get_credentials()
```

単一の設定は環境変数でも指定できます。list 型の `scopes` は JSON 配列として設定します。

```bash
export KIARINA_LIB_GOOGLE_TYPE="service_account"
export KIARINA_LIB_GOOGLE_SERVICE_ACCOUNT_FILE="~/key.json"
export KIARINA_LIB_GOOGLE_PROJECT_ID="your-project-id"
export KIARINA_LIB_GOOGLE_SCOPES='["https://www.googleapis.com/auth/cloud-platform"]'
```

### Integrating Authentication into Service Implementations

Google Cloud Storage など、Google 認証を必要とする service を実装する場合は、service 固有の設定に `google_settings_key` を持たせます。service は Google 認証設定の詳細を保持せず、client を生成するときに `get_credentials` へ設定キーを渡します。

```python
# _settings.py
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class GCSSettings(BaseSettings):
    google_settings_key: str | None = None


settings_manager = SettingsManager(GCSSettings)

# _services/my_service.py
from google.cloud.storage import Client

from kiarina.lib.google import get_credentials

from .._settings import GCSSettings


class MyService:
    def __init__(self, settings: GCSSettings) -> None:
        self.settings: GCSSettings = settings
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client(
                credentials=get_credentials(self.settings.google_settings_key)
            )

        return self._client
```

このパターンでは、service の設定が利用する認証設定だけを選択し、認証方式・鍵ファイル・scope などは `kiarina.lib.google` 側へ分離できます。`google_settings_key=None` の場合は、`settings_manager` の default 設定が使用されます。

### Configuring Google Gen AI Clients

`get_genai_options` は `GoogleSettings` から Google Gen AI client の初期化 options を生成します。

```python
from google import genai

from kiarina.lib.google import get_genai_options

client = genai.Client(**get_genai_options("gemini"))
```

`vertexai=True` と `api_key` を設定すると Vertex AI Express Mode になります。この場合、現在の Express Mode 仕様に合わせて `project` と `location` は options に含めません。

```yaml
kiarina.lib.google:
  configs:
    express:
      type: api_key
      vertexai: true
      api_key: ${GOOGLE_API_KEY}
```

`vertexai=True` で `api_key` がない場合は、Google credentials を使う Vertex AI mode になります。`project_id` と `location` は、設定されている場合だけ options に含まれます。

### Generating a Self-Signed JWT

サービスアカウントなどの署名可能な認証情報から、ネットワーク通信を行わずに自己署名 JWT を生成します。

```python
from kiarina.lib.google import GoogleSettings, get_self_signed_jwt

jwt_token = get_self_signed_jwt(
    settings=GoogleSettings(
        type="service_account",
        service_account_file="~/key.json",
    ),
    audience="https://your-service.example.com/",
)
```

## API Reference

### `kiarina.lib.google`

```python
from kiarina.lib.google import (
    Credentials,
    CredentialsCache,
    CredentialsJSONString,
    GoogleSettings,
    SelfSignedJWT,
    get_credentials,
    get_default_credentials,
    get_genai_options,
    get_self_signed_jwt,
    get_service_account_credentials,
    get_user_account_credentials,
    settings_manager,
)
```

#### `get_credentials`

```python
def get_credentials(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    scopes: list[str] | None = None,
    cache: CredentialsCache | None = None,
) -> Credentials: ...
```

設定に応じて ADC、サービスアカウント、またはユーザーアカウントの認証情報を取得し、必要に応じてサービスアカウントの権限を借用します。

`settings` は `settings_key` より優先され、`scopes` は `settings.scopes` より優先されます。

- `ValueError`: 権限借用に必要な scope がない場合、認証情報の入力がない場合、ファイルが存在しない場合、または `type` がサポートされていない場合

#### `get_genai_options`

```python
def get_genai_options(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    scopes: list[str] | None = None,
    cache: CredentialsCache | None = None,
) -> dict[str, Any]: ...
```

Google Gen AI client に渡す options を生成します。`vertexai=True` と `api_key` がある場合は Express Mode として `{"vertexai": True, "api_key": ...}` のみを返します。`vertexai=False` は Gemini Developer API mode として扱います。`vertexai=None` の場合、`type="api_key"` は Gemini Developer API mode、それ以外は Vertex AI credentials mode になります。

#### `get_self_signed_jwt`

```python
def get_self_signed_jwt(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    audience: str,
) -> SelfSignedJWT: ...
```

解決した署名可能な認証情報を使用して、`audience` 向けの自己署名 JWT を生成します。

#### `get_default_credentials`

```python
def get_default_credentials() -> (
    google.auth.compute_engine.credentials.Credentials
    | google.oauth2.credentials.Credentials
    | google.oauth2.service_account.Credentials
): ...
```

Google Auth Library の Application Default Credentials を取得します。

#### `get_service_account_credentials`

```python
def get_service_account_credentials(
    *,
    service_account_file: str | os.PathLike[str] | None = None,
    service_account_data: dict[str, object] | None = None,
    scopes: list[str] | None = None,
) -> google.oauth2.service_account.Credentials: ...
```

`service_account_data`、`service_account_file` の優先順でサービスアカウント認証情報を生成し、指定された scope を適用します。ファイルパスでは環境変数と `~` を展開します。

- `ValueError`: 入力がない場合、または指定されたファイルが存在しない場合

#### `get_user_account_credentials`

```python
def get_user_account_credentials(
    *,
    authorized_user_file: str | os.PathLike[str] | None = None,
    authorized_user_data: dict[str, object] | None = None,
    scopes: list[str] | None = None,
    cache: CredentialsCache | None = None,
) -> google.oauth2.credentials.Credentials: ...
```

cache、`authorized_user_data`、`authorized_user_file` の優先順でユーザー認証情報を取得します。認証情報が期限切れで refresh token を持つ場合は更新し、有効な新規・更新済み認証情報を cache に保存します。

- `ValueError`: 入力がない場合、または指定されたファイルが存在しない場合

#### `GoogleSettings`

```python
class GoogleSettings(BaseSettings):
    type: Literal[
        "default",
        "service_account",
        "user_account",
        "api_key",
    ] = "default"
    project_id: str | None = None
    impersonate_service_account: str | None = None
    scopes: list[str] = Field(default_factory=list)
    service_account_email: str | None = None
    service_account_file: str | None = None
    service_account_data: SecretStr | None = None
    user_account_email: str | None = None
    client_secret_file: str | None = None
    client_secret_data: SecretStr | None = None
    authorized_user_file: str | None = None
    authorized_user_data: SecretStr | None = None
    api_key: SecretStr | None = None
    vertexai: bool | None = None
    location: str | None = None

    def get_service_account_data(self) -> dict[str, Any] | None: ...

    def get_client_secret_data(self) -> dict[str, Any] | None: ...

    def get_authorized_user_data(self) -> dict[str, Any] | None: ...
```

`KIARINA_LIB_GOOGLE_` prefix の環境変数に対応する認証設定モデルです。file フィールドの `~` は model validation 時に展開され、data フィールドの helper method は `SecretStr` 内の JSON を dictionary に変換します。

| Field | Description |
| --- | --- |
| `type` | 使用する認証方式 |
| `project_id` | Google Cloud のプロジェクト ID |
| `impersonate_service_account` | 権限を借用するサービスアカウントのメールアドレス |
| `scopes` | 要求する OAuth スコープ |
| `service_account_email` | サービスアカウントのメールアドレス |
| `service_account_file` | サービスアカウントキーファイルのパス |
| `service_account_data` | サービスアカウントキーの JSON 文字列 |
| `user_account_email` | ユーザーアカウントのメールアドレス |
| `client_secret_file` | OAuth クライアントシークレットファイルのパス |
| `client_secret_data` | OAuth クライアントシークレットの JSON 文字列 |
| `authorized_user_file` | 認証済みユーザー情報ファイルのパス |
| `authorized_user_data` | 認証済みユーザー情報の JSON 文字列 |
| `api_key` | Google API キー |
| `vertexai` | Google Gen AI client で Vertex AI を使うかどうか |
| `location` | Google Gen AI Vertex AI client の Google Cloud location |

`get_service_account_data`、`get_client_secret_data`、`get_authorized_user_data` は、対応する JSON 文字列を dictionary に変換します。値がない場合は `None` を返し、不正な JSON の場合は `json.JSONDecodeError` を送出します。

`get_credentials` が認証情報の生成に使用するフィールドは、`type`、`impersonate_service_account`、`scopes`、`service_account_file`、`service_account_data`、`authorized_user_file`、`authorized_user_data` です。`get_genai_options` は `type`、`api_key`、`vertexai`、`project_id`、`location` も参照します。その他のフィールドは、この設定モデルを共有する関連サービスから参照できます。

`type="api_key"` と `api_key` は API key を安全に設定へ保持するために使用できますが、`get_credentials` は API key を Google credentials へ変換せず、`ValueError` を送出します。

#### `settings_manager`

```python
settings_manager: SettingsManager[GoogleSettings] = SettingsManager(
    GoogleSettings,
    multi=True,
)
```

複数の名前付き `GoogleSettings` を管理する公開 instance です。

#### `CredentialsCache`

```python
class CredentialsCache(Protocol):
    def get(self) -> CredentialsJSONString | None: ...

    def set(self, value: CredentialsJSONString) -> None: ...
```

ユーザー認証情報の JSON cache を読み書きする interface です。

#### Type aliases

```python
Credentials: TypeAlias = (
    google.auth.compute_engine.credentials.Credentials
    | google.oauth2.service_account.Credentials
    | google.oauth2.credentials.Credentials
    | google.auth.impersonated_credentials.Credentials
)
CredentialsJSONString: TypeAlias = str
SelfSignedJWT: TypeAlias = str
```

| Type | Description |
| --- | --- |
| `Credentials` | このパッケージが返す Google credentials の union |
| `CredentialsJSONString` | cache に保存する認証情報の JSON 文字列 |
| `SelfSignedJWT` | 自己署名 JWT 文字列 |
