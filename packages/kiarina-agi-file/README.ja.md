# kiarina-agi-file

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-agi-file.svg)](https://badge.fury.io/py/kiarina-agi-file)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-agi-file.svg)](https://pypi.org/project/kiarina-agi-file/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> AI agent の file を local filesystem に、asset を交換可能な asset store に保存し、access policy と local cache を通して安全に取得するための package です。

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

#### `asset-repository-gcs`

Google Cloud Storage asset repository に使用します。

| Package | Version | License |
| --- | --- | --- |
| [google-cloud-storage](https://github.com/googleapis/python-storage) | `>=3.4.0` | [Apache-2.0](https://github.com/googleapis/python-storage/blob/main/LICENSE) |

## Installation

Local filesystem のみを使用する場合:

```bash
pip install kiarina-agi-file
```

Google Cloud Storage も使用する場合:

```bash
pip install "kiarina-agi-file[asset-repository-gcs]"
```

## Features

- **Local file storage**
  Application data directory と cache directory に file を保存し、正規表現でアクセス可能な path を制限します。
- **Pluggable asset storage**
  Asset store の実装に依存しない async API を提供し、implementation を import path で登録できます。
- **Local asset cache**
  URI ごとに取得結果を cache し、TTL 経過後に再取得します。
- **Unified file resolution**
  URI と local file path を自動判別し、どちらも `FileBlob` として取得します。

### Store Local Files

最初に application name を設定します。既定の data path と cache path は、application の user directory と `RunContext.agent_id` から生成されます。

```python
from kiarina.agi.base.run_context import RunContext
from kiarina.agi.file.local_repository import create_local_repository
from kiarina.utils.app import configure

configure("example-app", "example-author")
run_context = RunContext()
repository = create_local_repository(run_context)

file_path = repository.generate_data_path("documents/example.txt")
file_blob = await repository.set(file_path, "text/plain", b"hello")
loaded = await repository.get(file_path)
```

`FilePathPolicy.allowed_file_path_patterns` は正規表現の完全一致です。既定値はすべての path を許可するため、untrusted な path を扱う application では明示的に制限してください。

### Store Assets

既定の `local` preset は local filesystem を使用します。保存結果と取得結果は local asset cache 内の `FileBlob` です。

```python
from kiarina.agi.base.run_context import RunContext
from kiarina.agi.file.asset_repository import create_asset_repository
from kiarina.utils.app import configure

configure("example-app", "example-author")
repository = create_asset_repository(RunContext())

uri = repository.generate_data_uri("documents/example.txt")
cached_file = await repository.set(uri, "text/plain", b"hello")
loaded = await repository.get(uri)
```

`get(..., ignore_cache=True)` は cache を読まずに backend から取得し、cache を更新します。`delete()` は backend と cache の両方から削除します。

### Use an Asset Store Implementation

Asset store は preset または custom implementation として選択します。この package には `local` と `gcs` preset が含まれます。

例えば、Google Cloud Storage を使用する場合は `gcs` preset と `gs://` URI 用の policy を設定します。`{organization_id}`、`{user_id}`、`{agent_id}` は `RunContext` の値に展開されます。

```bash
export KIARINA_AGI_ASSET_REPOSITORY_DEFAULT=gcs
export KIARINA_AGI_ASSET_REPOSITORY_URI_POLICY='{
  "allowed_uri_patterns": ["gs://example-bucket/{agent_id}/.*"],
  "data_dir_uri_template": "gs://example-bucket/{agent_id}/data",
  "cache_dir_uri_template": "gs://example-bucket/{agent_id}/cache"
}'
```

認証は `kiarina-lib-google` の設定から解決されます。特定の設定 key を使用する場合:

```bash
export KIARINA_AGI_ASSET_REPOSITORY_IMPL_GCS_GOOGLE_AUTH_SETTINGS_KEY=service_account
```

### Resolve a URI or File Path

```python
from kiarina.agi.file.file import get_file_blob

file_blob = await get_file_blob(
    "gs://example-bucket/agent-1/data/example.txt",
    run_context=run_context,
)
```

URI は configured asset repository、その他の文字列は local repository から取得します。対象が存在しない場合は `None` を返します。

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

`resolve_file_path()` は environment variable と `~` を展開し、absolute path を返します。許可されていない path に対する操作は `PermissionError` を送出します。

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

    # AssetRepository のすべての method を実装します。

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

`AssetRepositorySpecifier` は repository name、または `"{name}?{config}"` 形式の文字列です。URI pattern が未設定の場合は `ValueError`、許可されていない URI に対する操作は `PermissionError` を送出します。

### `kiarina.agi.file.asset_repository_impl.local`

```python
from kiarina.agi.file.asset_repository_impl.local import LocalAssetRepository

class LocalAssetRepository(BaseAssetRepository):
    @property
    def template_variables(self) -> dict[str, str]: ...

    @property
    def local_repository(self) -> LocalRepository: ...
```

`LocalAssetRepository` は `BaseAssetRepository` の storage 操作を local filesystem に実装します。download URL は `file://` URL です。

### `kiarina.agi.file.asset_repository_impl.gcs`

この module の import には `asset-repository-gcs` extra が必要です。

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
