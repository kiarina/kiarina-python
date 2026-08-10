# kiarina-agi-file

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-agi-file.svg)](https://badge.fury.io/py/kiarina-agi-file)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-agi-file.svg)](https://pypi.org/project/kiarina-agi-file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for storing AI agent files in a local filesystem and assets in a pluggable asset store, with safe retrieval through access policies and a local cache.

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.4.0` | [MIT](../../LICENSE) |
| [kiarina-lib-google](../kiarina-lib-google/) | `>=2.3.1` | [MIT](../../LICENSE) |
| [kiarina-utils-app](../kiarina-utils-app/) | `>=2.4.0` | [MIT](../../LICENSE) |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.3.0` | [MIT](../../LICENSE) |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | [MIT](../../LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

### Optional Dependencies

| Package | Version | License | Extras |
| --- | --- | --- | --- |
| [google-cloud-storage](https://github.com/googleapis/python-storage) | `>=3.4.0` | [Apache-2.0](https://github.com/googleapis/python-storage/blob/main/LICENSE) | `asset-repository-gcs` |

The `all` Extra installs every optional dependency listed above.

## Installation

For local filesystem storage only:

```bash
pip install kiarina-agi-file
```

To also use Google Cloud Storage:

```bash
pip install "kiarina-agi-file[all]"
```

## Features

- **Local file storage**
  Stores files in application data and cache directories and restricts accessible paths with regular expressions.
- **Pluggable asset storage**
  Provides an async API independent of the asset store implementation and supports implementations registered by import path.
- **Local asset cache**
  Caches retrieved content by URI and fetches it again after its TTL expires.
- **Unified file resolution**
  Detects URIs and local file paths and returns either as a `FileBlob`.

### Store Local Files

Configure the application name first. The default data and cache paths are generated from the application's user directories and `RunContext.agent_id`.

```python
from kiarina.agi.run_context import RunContext
from kiarina.agi.local_repository import create_local_repository
from kiarina.utils.app import configure

configure("example-app", "example-author")
run_context = RunContext()
repository = create_local_repository(run_context)

file_path = repository.generate_data_path("documents/example.txt")
file_blob = await repository.set(file_path, "text/plain", b"hello")
loaded = await repository.get(file_path)
```

`FilePathPolicy.allowed_file_path_patterns` uses full regular-expression matches. Its default allows every path, so applications that handle untrusted paths should restrict it explicitly.

### Store Assets

The default `local` preset uses the local filesystem. Stored and retrieved values are `FileBlob` objects in the local asset cache.

```python
from kiarina.agi.run_context import RunContext
from kiarina.agi.asset_repository import create_asset_repository
from kiarina.utils.app import configure

configure("example-app", "example-author")
repository = create_asset_repository(RunContext())

uri = repository.generate_data_uri("documents/example.txt")
cached_file = await repository.set(uri, "text/plain", b"hello")
loaded = await repository.get(uri)
```

`get(..., ignore_cache=True)` skips reading the cache, retrieves the asset from the backend, and refreshes the cache. `delete()` removes the asset from both the backend and the cache.

### Use an Asset Store Implementation

Select an asset store as a preset or custom implementation. This package includes the `local` and `gcs` presets.

For example, to use Google Cloud Storage, select the `gcs` preset and configure a policy for `gs://` URIs. `{organization_id}`, `{user_id}`, and `{agent_id}` are expanded from the `RunContext`.

```bash
export KIARINA_AGI_ASSET_REPOSITORY_DEFAULT=gcs
export KIARINA_AGI_ASSET_REPOSITORY_URI_POLICY='{
  "allowed_uri_patterns": ["gs://example-bucket/{agent_id}/.*"],
  "data_dir_uri_template": "gs://example-bucket/{agent_id}/data",
  "cache_dir_uri_template": "gs://example-bucket/{agent_id}/cache"
}'
```

Credentials are resolved from `kiarina-lib-google` settings. To use a specific settings key:

```bash
export KIARINA_AGI_ASSET_REPOSITORY_IMPL_GCS_GOOGLE_AUTH_SETTINGS_KEY=service_account
```

### Resolve a URI or File Path

```python
from kiarina.agi.file import get_file_blob

file_blob = await get_file_blob(
    "gs://example-bucket/agent-1/data/example.txt",
    run_context=run_context,
)
```

URIs use the configured asset repository; other strings use the local repository. The function returns `None` when the target does not exist.

## API Reference

### `kiarina.agi.file`

```python
from kiarina.agi.file import FilePath, URIOrFilePath, get_file_blob
```

```python
async def get_file_blob(
    uri_or_file_path: URIOrFilePath,
    *,
    run_context: RunContext,
) -> FileBlob | None: ...

FilePath: TypeAlias = str
URIOrFilePath: TypeAlias = str
```

### `kiarina.agi.local_repository`

```python
from kiarina.agi.local_repository import (
    FilePathPolicy,
    LocalArea,
    LocalRepository,
    LocalRepositorySettings,
    create_local_repository,
    resolve_file_path,
    settings_manager,
)
```

```python
def create_local_repository(run_context: RunContext) -> LocalRepository: ...

def resolve_file_path(file_path: str | os.PathLike[str]) -> str: ...

class LocalRepository:
    def __init__(
        self,
        settings: LocalRepositorySettings,
        *,
        run_context: RunContext,
    ) -> None: ...

    @property
    def template_variables(self) -> dict[str, str]: ...

    @property
    def file_path_policy(self) -> FilePathPolicy: ...

    @property
    def data_dir(self) -> str: ...

    @property
    def cache_dir(self) -> str: ...

    def generate_data_path(self, relative_path: str | os.PathLike[str]) -> str: ...

    def generate_cache_path(self, relative_path: str | os.PathLike[str]) -> str: ...

    def generate_time_based_dir_path(
        self,
        *,
        sub_dir_path: str | os.PathLike[str] = "log",
        area: LocalArea = "data",
    ) -> str: ...

    def generate_time_based_file_path(
        self,
        file_name: str,
        *,
        sub_dir_path: str | os.PathLike[str] = "log",
        area: LocalArea = "data",
    ) -> str: ...

    def is_valid_file_path(self, file_path: str | os.PathLike[str]) -> bool: ...

    def validate_file_path(self, file_path: str | os.PathLike[str]) -> None: ...

    async def exists(self, file_path: str | os.PathLike[str]) -> bool: ...

    async def get(self, file_path: str | os.PathLike[str]) -> FileBlob | None: ...

    async def set(
        self,
        file_path: str | os.PathLike[str],
        mime_type: str,
        raw_data: bytes,
        *,
        only_not_exists: bool = False,
    ) -> FileBlob: ...

    async def delete(self, file_path: str | os.PathLike[str]) -> None: ...

class FilePathPolicy(BaseModel):
    allowed_file_path_patterns: list[str] = [".*"]
    data_dir_path_template: str = "{user_data_dir}/agents/{agent_id}"
    cache_dir_path_template: str = "{user_cache_dir}/agents/{agent_id}"

class LocalRepositorySettings(BaseSettings):
    file_path_policy: FilePathPolicy = FilePathPolicy()

LocalArea = Literal["data", "cache"]
settings_manager: SettingsManager[LocalRepositorySettings]
```

`resolve_file_path()` expands environment variables and `~`, then returns an absolute path. Operations on a disallowed path raise `PermissionError`.

### `kiarina.agi.asset_cache`

```python
from kiarina.agi.asset_cache import (
    AssetCache,
    AssetCacheSettings,
    create_asset_cache,
    settings_manager,
)
```

```python
def create_asset_cache(run_context: RunContext) -> AssetCache: ...

class AssetCache:
    def __init__(
        self,
        settings: AssetCacheSettings,
        *,
        run_context: RunContext,
    ) -> None: ...

    @property
    def local_repository(self) -> LocalRepository: ...

    async def get(self, uri: str) -> FileBlob | None: ...

    async def set(self, uri: str, mime_type: str, raw_data: bytes) -> FileBlob: ...

    async def delete(self, uri: str) -> None: ...

class AssetCacheSettings(BaseSettings):
    hash_algorithm: str = "sha256"
    cache_ttl: int = 86400

settings_manager: SettingsManager[AssetCacheSettings]
```

### `kiarina.agi.asset_repository`

```python
from kiarina.agi.asset_repository import (
    AssetArea,
    AssetRepository,
    AssetRepositoryName,
    AssetRepositorySettings,
    AssetRepositorySpecifier,
    BaseAssetRepository,
    CachedFileBlob,
    URIPolicy,
    asset_repository_registry,
    create_asset_repository,
    settings_manager,
)
```

```python
def create_asset_repository(run_context: RunContext) -> AssetRepository: ...

class AssetRepository(Protocol):
    uri_policy: URIPolicy
    run_context: RunContext

    @property
    def asset_cache(self) -> AssetCache: ...

    def generate_data_uri(self, relative_path: str) -> str: ...

    def generate_cache_uri(self, relative_path: str) -> str: ...

    def generate_time_based_uri(
        self,
        file_name: str | None = None,
        *,
        sub_dir_path: str = "log",
        area: AssetArea = "data",
    ) -> str: ...

    def is_valid_uri(self, uri: str) -> bool: ...

    def validate_uri(self, uri: str) -> None: ...

    async def exists(self, uri: str) -> bool: ...

    async def get(
        self,
        uri: str,
        *,
        ignore_cache: bool = False,
    ) -> CachedFileBlob | None: ...

    async def set(
        self,
        uri: str,
        mime_type: str,
        raw_data: bytes,
        *,
        only_not_exists: bool = False,
    ) -> CachedFileBlob: ...

    async def delete(self, uri: str) -> None: ...

    async def generate_download_url(
        self,
        uri: str,
        *,
        expire_seconds: int = 86400,
    ) -> str: ...

class BaseAssetRepository(AssetRepository):
    def __init__(self) -> None: ...

    @property
    def uri_policy(self) -> URIPolicy: ...

    @uri_policy.setter
    def uri_policy(self, uri_policy: URIPolicy) -> None: ...

    @property
    def run_context(self) -> RunContext: ...

    @run_context.setter
    def run_context(self, run_context: RunContext) -> None: ...

    @property
    def template_variables(self) -> dict[str, str]: ...

    @property
    def asset_cache(self) -> AssetCache: ...

    @property
    def data_uri(self) -> str: ...

    @property
    def cache_uri(self) -> str: ...

    # Implements every AssetRepository method.

class URIPolicy(BaseModel):
    allowed_uri_patterns: list[str] = []
    data_dir_uri_template: str = "{invalid}"
    cache_dir_uri_template: str = "{invalid}"

class AssetRepositorySettings(BaseSettings):
    default: AssetRepositorySpecifier = "local"
    presets: dict[AssetRepositoryName, ImportPath] = <local and gcs presets>
    customs: dict[AssetRepositoryName, ImportPath] = {}
    uri_policy: URIPolicy = <local asset policy>

AssetArea = Literal["data", "cache"]
AssetRepositoryName: TypeAlias = str
AssetRepositorySpecifier: TypeAlias = AssetRepositoryName | str
CachedFileBlob: TypeAlias = FileBlob
asset_repository_registry: ComponentRegistry[AssetRepository]
settings_manager: SettingsManager[AssetRepositorySettings]
```

`AssetRepositorySpecifier` is a repository name or a string in the `"{name}?{config}"` form. An absent URI pattern raises `ValueError`; operations on a disallowed URI raise `PermissionError`.

### `kiarina.agi.asset_repository_impl.local`

```python
from kiarina.agi.asset_repository_impl.local import LocalAssetRepository

class LocalAssetRepository(BaseAssetRepository):
    @property
    def template_variables(self) -> dict[str, str]: ...

    @property
    def local_repository(self) -> LocalRepository: ...
```

`LocalAssetRepository` implements the `BaseAssetRepository` storage operations on the local filesystem. Its download URL is a `file://` URL.

### `kiarina.agi.asset_repository_impl.gcs`

Importing this module requires the `asset-repository-gcs` extra.

```python
from kiarina.agi.asset_repository_impl.gcs import (
    GCSAssetRepository,
    GCSAssetRepositorySettings,
    create_gcs_asset_repository,
    settings_manager,
)
```

```python
def create_gcs_asset_repository(**kwargs: Any) -> GCSAssetRepository: ...

class GCSAssetRepository(BaseAssetRepository):
    def __init__(self, settings: GCSAssetRepositorySettings) -> None: ...

    @property
    def client(self) -> google.cloud.storage.Client: ...

class GCSAssetRepositorySettings(BaseSettings):
    google_auth_settings_key: str | None = None

settings_manager: SettingsManager[GCSAssetRepositorySettings]
```
