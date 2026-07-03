# kiarina-agi-file

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-agi-file.svg)](https://badge.fury.io/py/kiarina-agi-file)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-agi-file.svg)](https://pypi.org/project/kiarina-agi-file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> Provides safe local filesystem and Google Cloud Storage asset persistence with local caching for AI agents.

## Dependencies

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

| Extra | Package | Version | License |
| --- | --- | --- | --- |
| `asset-repository-gcs` | [google-cloud-storage](https://github.com/googleapis/python-storage) | `>=3.4.0` | [Apache-2.0](https://github.com/googleapis/python-storage/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-agi-file
```

To use the Google Cloud Storage asset repository:

```bash
pip install 'kiarina-agi-file[asset-repository-gcs]'
```

## Features

- **Local repository**
  Restricts access to allowed paths and separates data and cache directories.
- **Asset repository**
  Uses the same API for local filesystems and Google Cloud Storage.
- **Asset cache**
  Stores remote assets in a local cache with a TTL.
- **File resolution**
  Resolves a URI or local file path to a `FileBlob`.

### Local Repository

```python
from kiarina.agi.base.run_context import RunContext
from kiarina.agi.file.local_repository import create_local_repository
from kiarina.utils.app import configure

configure("example-app", "example-author")
repository = create_local_repository(RunContext())
file_path = repository.generate_data_path("documents/example.txt")
```

### Asset Repository

The available presets are `local` and `gcs`. `AssetRepositorySettings.uri_policy` restricts accessible URIs.

```python
from kiarina.agi.file.asset_repository import create_asset_repository

repository = create_asset_repository(RunContext())
uri = repository.generate_data_uri("documents/example.txt")
file_blob = await repository.set(uri, "text/plain", b"hello")
```

## API Reference

### `kiarina.agi.file.file`

```python
from kiarina.agi.file.file import FilePath, URIOrFilePath, get_file_blob
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

### `kiarina.agi.file.local_repository`

```python
from kiarina.agi.file.local_repository import (
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

### `kiarina.agi.file.asset_cache`

```python
from kiarina.agi.file.asset_cache import (
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

### `kiarina.agi.file.asset_repository`

```python
from kiarina.agi.file.asset_repository import (
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

`BaseAssetRepository` implements the public `AssetRepository` methods and properties and delegates storage-specific operations to subclasses.

### `kiarina.agi.file.asset_repository_impl.local`

```python
from kiarina.agi.file.asset_repository_impl.local import LocalAssetRepository

class LocalAssetRepository(BaseAssetRepository):
    pass
```

`LocalAssetRepository` implements the public API inherited from `BaseAssetRepository`.

### `kiarina.agi.file.asset_repository_impl.gcs`

```python
from kiarina.agi.file.asset_repository_impl.gcs import (
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
