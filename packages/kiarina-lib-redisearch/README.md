# kiarina-lib-redisearch

[![PyPI](https://img.shields.io/pypi/v/kiarina-lib-redisearch.svg)](https://pypi.org/project/kiarina-lib-redisearch/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

English | [日本語](README.ja.md)

> [!NOTE]
> Provides synchronous and asynchronous RediSearch clients, search filters, and index schemas.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [NumPy](https://github.com/numpy/numpy) | `>=2.3.2` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |
| [redis-py](https://github.com/redis/redis-py) | `>=6.4.0` | [MIT](https://github.com/redis/redis-py/blob/master/LICENSE) |

## Installation

```bash
pip install kiarina-lib-redisearch
```

## Features

- **Index management**
  Create, drop, reset, and migrate indexes.
- **Document operations**
  Store, retrieve, and delete documents as Redis hashes.
- **Filtered search**
  Build tag, numeric, and text conditions with typed objects or condition lists.
- **Vector search**
  Run nearest-neighbor searches against FLAT or HNSW indexes.
- **Synchronous and asynchronous APIs**
  Use the same operations through `kiarina.lib.redisearch` and `kiarina.lib.redisearch.asyncio`.

### Configuring an Index

Environment variables use the `KIARINA_LIB_REDISEARCH_` prefix.

```bash
export KIARINA_LIB_REDISEARCH_KEY_PREFIX="article:"
export KIARINA_LIB_REDISEARCH_INDEX_NAME="articles"
export KIARINA_LIB_REDISEARCH_PROTECT_INDEX_DELETION="false"
```

User configuration through `pydantic-settings-manager` can hold multiple named index settings.

```yaml
kiarina.lib.redisearch:
  default: articles
  configs:
    articles:
      key_prefix: "article:"
      index_name: articles
      protect_index_deletion: false
```

### Defining a Schema

```python
from kiarina.lib.redisearch_schema import RedisearchFieldDicts

field_dicts: RedisearchFieldDicts = [
    {"type": "tag", "name": "category"},
    {"type": "text", "name": "title", "sortable": True},
    {"type": "numeric", "name": "price", "sortable": True},
    {
        "type": "vector",
        "name": "embedding",
        "algorithm": "HNSW",
        "dims": 1536,
        "distance_metric": "COSINE",
    },
]
```

`decode_responses=False` is required because Redis stores vectors as bytes.

### Using the Synchronous Client

```python
from redis import Redis

from kiarina.lib.redisearch import create_redisearch_client

redis = Redis.from_url("redis://localhost:6379", decode_responses=False)
client = create_redisearch_client(field_dicts=field_dicts, redis=redis)

client.create_index()
client.set(
    {
        "id": "1",
        "category": "news",
        "title": "Example",
        "price": 100,
        "embedding": [0.1] * 1536,
    }
)
result = client.find(return_fields=["category", "title", "price"])
```

### Using the Asynchronous Client

```python
from redis.asyncio import Redis

from kiarina.lib.redisearch.asyncio import create_redisearch_client

redis = Redis.from_url("redis://localhost:6379", decode_responses=False)
client = create_redisearch_client(field_dicts=field_dicts, redis=redis)

await client.create_index()
result = await client.find(return_fields=["category", "title", "price"])
```

### Filtering Documents

```python
from kiarina.lib.redisearch_filter import Numeric, Tag, Text

filter = (Tag("category") == "news") & (Numeric("price") < 1000)
result = client.find(filter=filter)

filter = Text("title") % "python*"
result = client.find(filter=filter)

filter = (Tag("color") == "blue") & (Numeric("price") < 100)
print(str(filter))
# (@color:{blue} @price:[-inf (100])
```

Conditions in a list are joined with AND.

```python
result = client.find(
    filter=[
        ["category", "in", ["news", "guide"]],
        ["price", "<", 1000],
        ["title", "like", "python*"],
    ]
)
```

### Searching by Vector

```python
result = client.search(
    vector=[0.1] * 1536,
    filter=Tag("category") == "news",
    limit=10,
    return_fields=["title", "price"],
)
```

## API Reference

### `kiarina.lib.redisearch`

```python
from kiarina.lib.redisearch import (
    RedisearchClient,
    RedisearchSettings,
    create_redisearch_client,
    settings_manager,
)
```

#### `create_redisearch_client`

```python
def create_redisearch_client(
    settings_key: str | None = None,
    *,
    field_dicts: RedisearchFieldDicts,
    redis: redis.Redis,
) -> RedisearchClient: ...
```

Creates a client from a settings key, field definitions, and a synchronous Redis client.

#### `RedisearchClient`

```python
class RedisearchClient:
    def __init__(
        self,
        settings: RedisearchSettings,
        *,
        schema: RedisearchSchema,
        redis: redis.Redis,
    ) -> None: ...

    def exists_index(self) -> bool: ...
    def create_index(self) -> None: ...
    def drop_index(self, *, delete_documents: bool = False) -> bool: ...
    def reset_index(self) -> None: ...
    def migrate_index(self) -> None: ...
    def get_info(self) -> InfoResult: ...

    def set(self, mapping: dict[str, Any], *, id: str | None = None) -> None: ...
    def delete(self, id: str) -> None: ...
    def get(self, id: str) -> Document | None: ...

    def count(
        self,
        *,
        filter: RedisearchFilter | RedisearchFilterConditions | None = None,
    ) -> SearchResult: ...

    def find(
        self,
        *,
        filter: RedisearchFilter | RedisearchFilterConditions | None = None,
        sort_by: str | None = None,
        sort_desc: bool = False,
        offset: int | None = None,
        limit: int | None = None,
        return_fields: list[str] | None = None,
    ) -> SearchResult: ...

    def search(
        self,
        *,
        vector: list[float],
        filter: RedisearchFilter | RedisearchFilterConditions | None = None,
        offset: int | None = None,
        limit: int | None = None,
        return_fields: list[str] | None = None,
    ) -> SearchResult: ...

    def get_key(self, id: str) -> str: ...
```

`drop_index` returns `True` when the index is dropped. With `protect_index_deletion=True`, it leaves the index unchanged and returns `False`. When `id` is omitted from `set`, `mapping["id"]` is required. When `return_fields` is omitted from `find`, results contain IDs only.

#### `RedisearchSettings`

```python
class RedisearchSettings(BaseSettings):
    key_prefix: str = ""
    index_name: str = "default"
    protect_index_deletion: bool = False
```

#### `settings_manager`

```python
settings_manager: SettingsManager[RedisearchSettings]
```

Manages multiple named settings.

### `kiarina.lib.redisearch.asyncio`

```python
from kiarina.lib.redisearch.asyncio import (
    RedisearchClient,
    RedisearchSettings,
    create_redisearch_client,
    settings_manager,
)
```

#### `create_redisearch_client`

```python
def create_redisearch_client(
    settings_key: str | None = None,
    *,
    field_dicts: RedisearchFieldDicts,
    redis: redis.asyncio.Redis,
) -> RedisearchClient: ...
```

#### `RedisearchClient`

The asynchronous client uses the same arguments and return values as the synchronous client. Only methods that perform Redis I/O are `async`.

```python
class RedisearchClient:
    def __init__(
        self,
        settings: RedisearchSettings,
        *,
        schema: RedisearchSchema,
        redis: redis.asyncio.Redis,
    ) -> None: ...

    async def exists_index(self) -> bool: ...
    async def create_index(self) -> None: ...
    async def drop_index(self, *, delete_documents: bool = False) -> bool: ...
    async def reset_index(self) -> None: ...
    async def migrate_index(self) -> None: ...
    async def get_info(self) -> InfoResult: ...
    async def set(
        self,
        mapping: dict[str, Any],
        *,
        id: str | None = None,
    ) -> None: ...
    async def delete(self, id: str) -> None: ...
    async def get(self, id: str) -> Document | None: ...
    async def count(
        self,
        *,
        filter: RedisearchFilter | RedisearchFilterConditions | None = None,
    ) -> SearchResult: ...
    async def find(
        self,
        *,
        filter: RedisearchFilter | RedisearchFilterConditions | None = None,
        sort_by: str | None = None,
        sort_desc: bool = False,
        offset: int | None = None,
        limit: int | None = None,
        return_fields: list[str] | None = None,
    ) -> SearchResult: ...
    async def search(
        self,
        *,
        vector: list[float],
        filter: RedisearchFilter | RedisearchFilterConditions | None = None,
        offset: int | None = None,
        limit: int | None = None,
        return_fields: list[str] | None = None,
    ) -> SearchResult: ...
    def get_key(self, id: str) -> str: ...
```

`RedisearchSettings` and `settings_manager` are the same objects exported by the synchronous API.

### `kiarina.lib.redisearch_filter`

```python
from kiarina.lib.redisearch_filter import (
    Numeric,
    RedisearchFilter,
    RedisearchFilterConditions,
    Tag,
    Text,
    create_redisearch_filter,
)
```

#### `create_redisearch_filter`

```python
def create_redisearch_filter(
    *,
    filter: RedisearchFilter | RedisearchFilterConditions,
    schema: RedisearchSchema,
) -> RedisearchFilter | None: ...
```

Validates a condition list and converts it to filters joined with AND. Returns `None` for an empty list.

#### `Tag`

```python
class Tag:
    def __init__(self, field_name: str) -> None: ...
    def __eq__(
        self,
        other: list[str] | set[str] | tuple[str, ...] | str,
    ) -> RedisearchFilter: ...
    def __ne__(
        self,
        other: list[str] | set[str] | tuple[str, ...] | str,
    ) -> RedisearchFilter: ...
```

Creates equality and inequality conditions for single or multiple tag values.

```python
str(Tag("color") == "blue")          # @color:{blue}
str(Tag("color") == ["blue", "red"]) # @color:{blue|red}
str(Tag("color") != "blue")          # (-@color:{blue})
str(Tag("color") != ["blue", "red"]) # (-@color:{blue|red})
```

#### `Numeric`

```python
class Numeric:
    def __init__(self, field_name: str) -> None: ...
    def __eq__(self, other: int | float) -> RedisearchFilter: ...
    def __ne__(self, other: int | float) -> RedisearchFilter: ...
    def __gt__(self, other: int | float) -> RedisearchFilter: ...
    def __lt__(self, other: int | float) -> RedisearchFilter: ...
    def __ge__(self, other: int | float) -> RedisearchFilter: ...
    def __le__(self, other: int | float) -> RedisearchFilter: ...
```

Supports every numeric comparison operator.

```python
str(Numeric("price") == 100) # @price:[100 100]
str(Numeric("price") != 100) # (-@price:[100 100])
str(Numeric("price") > 100)  # @price:[(100 +inf]
str(Numeric("price") < 100)  # @price:[-inf (100]
str(Numeric("price") >= 100) # @price:[100 +inf]
str(Numeric("price") <= 100) # @price:[-inf 100]
```

#### `Text`

```python
class Text:
    def __init__(self, field_name: str) -> None: ...
    def __eq__(self, other: str) -> RedisearchFilter: ...
    def __ne__(self, other: str) -> RedisearchFilter: ...
    def __mod__(self, other: str) -> RedisearchFilter: ...
```

`==` and `!=` create exact-match conditions. `%` accepts a RediSearch text query, including wildcards.

```python
str(Text("title") == "hello") # @title:("hello")
str(Text("title") != "hello") # (-@title:"hello")
str(Text("title") % "*hello*") # @title:(*hello*)
```

#### `RedisearchFilter`

```python
class RedisearchFilter:
    def __init__(
        self,
        query: str | None = None,
        *,
        left: RedisearchFilter | None = None,
        operator: RedisearchFilterOperator | None = None,
        right: RedisearchFilter | None = None,
    ) -> None: ...
    def __and__(self, other: RedisearchFilter) -> RedisearchFilter: ...
    def __or__(self, other: RedisearchFilter) -> RedisearchFilter: ...
    def __str__(self) -> str: ...
```

`&` joins conditions with AND, while `|` joins them with OR.

```python
color = Tag("color") == "blue"
price = Numeric("price") < 100

str(color & price) # (@color:{blue} @price:[-inf (100])
str(color | price) # (@color:{blue} | @price:[-inf (100])
```

#### `RedisearchFilterConditions`

```python
RedisearchFilterConditions: TypeAlias = list[list[Any]]
```

Each condition contains `[field_name, operator, value]`. Multiple conditions are joined with AND.

```python
conditions: RedisearchFilterConditions = [
    ["color", "in", ["blue", "red"]],
    ["price", "<", 1000],
    ["title", "like", "*hello*"],
]
```

The following operators are available for each field type.

```python
tag_conditions: RedisearchFilterConditions = [
    ["color", "==", "blue"],
    ["color", "!=", "blue"],
    ["color", "in", ["blue", "red"]],
    ["color", "not in", ["blue", "red"]],
]

numeric_conditions: RedisearchFilterConditions = [
    ["price", "==", 1000],
    ["price", "!=", 1000],
    ["price", ">", 1000],
    ["price", "<", 1000],
    ["price", ">=", 1000],
    ["price", "<=", 1000],
]

text_conditions: RedisearchFilterConditions = [
    ["title", "==", "hello"],
    ["title", "!=", "hello"],
    ["title", "like", "*hello*"],
]
```

### `kiarina.lib.redisearch_schema`

```python
from kiarina.lib.redisearch_schema import (
    FieldSchema,
    FlatVectorFieldSchema,
    HNSWVectorFieldSchema,
    NumericFieldSchema,
    RedisearchFieldDicts,
    RedisearchSchema,
    TagFieldSchema,
    TextFieldSchema,
)
```

#### `RedisearchSchema`

```python
class RedisearchSchema(BaseModel):
    fields: list[FieldSchema] = []

    @property
    def field_names(self) -> list[str]: ...
    @property
    def vector_field(self) -> FlatVectorFieldSchema | HNSWVectorFieldSchema: ...
    def get_field(self, name: str) -> FieldSchema | None: ...
    def to_fields(self) -> list[redis.commands.search.field.Field]: ...
    @classmethod
    def from_field_dicts(cls, field_dicts: RedisearchFieldDicts) -> Self: ...
```

`vector_field` returns the first vector field and raises `ValueError` when none exists.

#### Field Schemas

```python
class NumericFieldSchema(BaseModel):
    name: str
    type: Literal["numeric"] = "numeric"
    no_index: bool = False
    sortable: bool | None = False
    def to_field(self) -> NumericField: ...

class TagFieldSchema(BaseModel):
    name: str
    type: Literal["tag"] = "tag"
    separator: str = ","
    case_sensitive: bool = False
    no_index: bool = False
    sortable: bool | None = False
    multiple: bool = False
    def to_field(self) -> TagField: ...

class TextFieldSchema(BaseModel):
    name: str
    type: Literal["text"] = "text"
    weight: float = 1
    no_stem: bool = False
    phonetic_matcher: str | None = None
    withsuffixtrie: bool = False
    no_index: bool = False
    sortable: bool | None = False
    def to_field(self) -> TextField: ...
```

`multiple` is a library-specific field used to decode stored values as multiple tags. It is not included in the RediSearch schema.

```python
class FlatVectorFieldSchema(BaseModel):
    name: str
    type: Literal["vector"] = "vector"
    dims: int
    datatype: Literal["FLOAT32", "FLOAT64"] = "FLOAT32"
    distance_metric: Literal["L2", "COSINE", "IP"] = "COSINE"
    initial_cap: int | None = None
    algorithm: Literal["FLAT"] = "FLAT"
    block_size: int | None = None
    def to_field(self) -> VectorField: ...

class HNSWVectorFieldSchema(BaseModel):
    name: str
    type: Literal["vector"] = "vector"
    dims: int
    datatype: Literal["FLOAT32", "FLOAT64"] = "FLOAT32"
    distance_metric: Literal["L2", "COSINE", "IP"] = "COSINE"
    initial_cap: int | None = None
    algorithm: Literal["HNSW"] = "HNSW"
    m: int = 16
    ef_construction: int = 200
    ef_runtime: int = 10
    epsilon: float = 0.01
    def to_field(self) -> VectorField: ...
```

#### Types

```python
FieldSchema: TypeAlias = (
    NumericFieldSchema
    | TagFieldSchema
    | TextFieldSchema
    | FlatVectorFieldSchema
    | HNSWVectorFieldSchema
)

RedisearchFieldDicts: TypeAlias = list[dict[str, Any]]
```
