# kiarina-lib-google

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-lib-google.svg)](https://badge.fury.io/py/kiarina-lib-google)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-lib-google.svg)](https://pypi.org/project/kiarina-lib-google/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for managing and providing Google credentials with pydantic-settings-manager.

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
  Retrieve Application Default Credentials (ADC) configured in the runtime environment.
- **Authenticating with a Service Account**
  Create service account credentials from a JSON key file or JSON data.
- **Authenticating with a User Account**
  Load authorized user data, refresh expired credentials, and cache credentials.
- **Impersonating a Service Account**
  Create short-lived credentials for a target service account from source credentials.
- **Managing Multiple Configurations**
  Centrally manage multiple authentication configurations with pydantic-settings-manager.
- **Integrating Authentication into Service Implementations**
  Inject an authentication settings key into a service that requires Google authentication and resolve credentials when creating its client.
- **Generating a Self-Signed JWT**
  Generate a self-signed JWT for a target service from signing credentials.

### Using Application Default Credentials

ADC searches the runtime environment for available credentials, including `GOOGLE_APPLICATION_CREDENTIALS`, local gcloud credentials, and the Google Cloud metadata server.

Credentials are searched in this order:

1. The credentials file referenced by `GOOGLE_APPLICATION_CREDENTIALS`
2. The local credentials file created by `gcloud auth application-default login`
3. The service account attached to the runtime, returned by the Google Cloud metadata server

See Google Cloud's [How Application Default Credentials works](https://cloud.google.com/docs/authentication/application-default-credentials) for details.

```python
from kiarina.lib.google import get_credentials

credentials = get_credentials()
```

### Authenticating with a Service Account

Use a service account JSON key file.

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

You can also pass a JSON string directly to the settings. `service_account_data` is retained as a `SecretStr`, so its secret value is not exposed in normal string representations.

```python
credentials = get_credentials(
    settings=GoogleSettings(
        type="service_account",
        service_account_data='{"type":"service_account","project_id":"example",...}',
    )
)
```

### Authenticating with a User Account

User accounts can use an authorized user file or JSON data. When `scopes` is omitted, scopes stored in the authorized user data are reused.

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

Implement `CredentialsCache` to store valid or refreshed credentials as a JSON string and reuse them during the next resolution.

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

Set `impersonate_service_account` to use the resolved credentials as source credentials for service account impersonation. Impersonation requires at least one scope.

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

The source principal requires the `roles/iam.serviceAccountTokenCreator` role on the target service account.

### Managing Multiple Configurations

`settings_manager` uses multi-configuration mode. In the pydantic-settings-manager v3 structured format, named settings are placed under `configs`.

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

Load the configuration during application bootstrap, then pass a configuration name to `get_credentials`.

```python
import yaml
from pydantic_settings_manager import load_user_configs

from kiarina.lib.google import get_credentials

with open("config.yaml", encoding="utf-8") as file:
    load_user_configs(yaml.safe_load(file) or {})

credentials = get_credentials("production")
```

To configure only this package directly, assign the structured format to `settings_manager.user_config`.

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

A single configuration can also be supplied through environment variables. Set list-valued `scopes` as a JSON array.

```bash
export KIARINA_LIB_GOOGLE_TYPE="service_account"
export KIARINA_LIB_GOOGLE_SERVICE_ACCOUNT_FILE="~/key.json"
export KIARINA_LIB_GOOGLE_PROJECT_ID="your-project-id"
export KIARINA_LIB_GOOGLE_SCOPES='["https://www.googleapis.com/auth/cloud-platform"]'
```

### Integrating Authentication into Service Implementations

When implementing a service that requires Google authentication, such as Google Cloud Storage, add `google_settings_key` to the service-specific settings. The service does not retain the details of the Google authentication configuration; it passes the settings key to `get_credentials` when creating the client.

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

This pattern lets the service settings select only the authentication configuration to use, while authentication methods, key files, and scopes remain separated in `kiarina.lib.google`. When `google_settings_key=None`, the default configuration from `settings_manager` is used.

### Generating a Self-Signed JWT

Generate a self-signed JWT from signing credentials such as a service account without making a network request.

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

Retrieve ADC, service account credentials, or user account credentials according to the settings, then optionally impersonate a service account.

`settings` takes precedence over `settings_key`, and `scopes` takes precedence over `settings.scopes`.

- `ValueError`: Impersonation has no scopes, credential input is missing, a file does not exist, or `type` is unsupported

#### `get_self_signed_jwt`

```python
def get_self_signed_jwt(
    settings_key: str | None = None,
    *,
    settings: GoogleSettings | None = None,
    audience: str,
) -> SelfSignedJWT: ...
```

Generate a self-signed JWT for `audience` with the resolved signing credentials.

#### `get_default_credentials`

```python
def get_default_credentials() -> (
    google.auth.compute_engine.credentials.Credentials
    | google.oauth2.credentials.Credentials
    | google.oauth2.service_account.Credentials
): ...
```

Retrieve Application Default Credentials from the Google Auth Library.

#### `get_service_account_credentials`

```python
def get_service_account_credentials(
    *,
    service_account_file: str | os.PathLike[str] | None = None,
    service_account_data: dict[str, object] | None = None,
    scopes: list[str] | None = None,
) -> google.oauth2.service_account.Credentials: ...
```

Create service account credentials in precedence order from `service_account_data` or `service_account_file`, then apply the specified scopes. Environment variables and `~` are expanded in file paths.

- `ValueError`: No input is provided or the specified file does not exist

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

Retrieve user credentials in precedence order from the cache, `authorized_user_data`, or `authorized_user_file`. Expired credentials with a refresh token are refreshed, and valid new or refreshed credentials are stored in the cache.

- `ValueError`: No input is provided or the specified file does not exist

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

    def get_service_account_data(self) -> dict[str, Any] | None: ...

    def get_client_secret_data(self) -> dict[str, Any] | None: ...

    def get_authorized_user_data(self) -> dict[str, Any] | None: ...
```

An authentication settings model that supports environment variables with the `KIARINA_LIB_GOOGLE_` prefix. The file fields expand `~` during model validation, and the data-field helper methods convert JSON held in `SecretStr` to dictionaries.

| Field | Description |
| --- | --- |
| `type` | Authentication method to use |
| `project_id` | Google Cloud project ID |
| `impersonate_service_account` | Email address of the service account to impersonate |
| `scopes` | OAuth scopes to request |
| `service_account_email` | Service account email address |
| `service_account_file` | Path to a service account key file |
| `service_account_data` | Service account key data as a JSON string |
| `user_account_email` | User account email address |
| `client_secret_file` | Path to an OAuth client secret file |
| `client_secret_data` | OAuth client secret data as a JSON string |
| `authorized_user_file` | Path to an authorized user credentials file |
| `authorized_user_data` | Authorized user credentials as a JSON string |
| `api_key` | Google API key |

`get_service_account_data`, `get_client_secret_data`, and `get_authorized_user_data` convert their corresponding JSON strings to dictionaries. They return `None` when no value is configured and raise `json.JSONDecodeError` for invalid JSON.

`get_credentials` uses `type`, `impersonate_service_account`, `scopes`, `service_account_file`, `service_account_data`, `authorized_user_file`, and `authorized_user_data` to create credentials. The remaining fields can retain related values for services that share this settings model.

`type="api_key"` and `api_key` can securely retain an API key in settings, but `get_credentials` does not convert API keys into Google credentials and raises `ValueError`.

#### `settings_manager`

```python
settings_manager: SettingsManager[GoogleSettings] = SettingsManager(
    GoogleSettings,
    multi=True,
)
```

The public instance that manages multiple named `GoogleSettings`.

#### `CredentialsCache`

```python
class CredentialsCache(Protocol):
    def get(self) -> CredentialsJSONString | None: ...

    def set(self, value: CredentialsJSONString) -> None: ...
```

An interface for reading and writing a JSON cache of user credentials.

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
| `Credentials` | Union of the Google credential types returned by this package |
| `CredentialsJSONString` | Credentials JSON string stored in a cache |
| `SelfSignedJWT` | Self-signed JWT string |
