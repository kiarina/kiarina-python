# kiarina-agi-data

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-data.svg)](https://pypi.org/project/kiarina-agi-data/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> `kiarina-agi-data` provides data models and transformations for AI agent messages, events, content, embeddings, and file metadata.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.5.0` | MIT |
| [kiarina-agi-file](../kiarina-agi-file/) | `>=2.5.0` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.3.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [jaxtyping](https://github.com/patrick-kidger/jaxtyping) | `>=0.3.3` | MIT |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | BSD-3-Clause |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | MIT |
| [ulid-py](https://github.com/ahawker/ulid) | `>=1.1.0` | Apache-2.0 |

## Installation

```bash
pip install kiarina-agi-data
```

## Features

- AI agent messages and streaming chunks
- Events and histories derived from messages
- Text and media content with file metadata
- Embedding normalization, similarity calculation, and search
- Tool schemas and execution states

## API Reference

Public APIs are available from the import paths below. Each class is a Pydantic model whose fields are available as typed constructor parameters.

### `kiarina.agi.data.chat_estimates`

```python
from kiarina.agi.data.chat_estimates import ChatEstimates
```

### `kiarina.agi.data.chat_limits`

```python
from kiarina.agi.data.chat_limits import ChatLimits, ChatLimitsSpecifier
```

### `kiarina.agi.data.content`

```python
from kiarina.agi.data.content import Content, dehydrate_content, hydrate_content

def dehydrate_content(content: Content, pool: FileInfoPool) -> tuple[Content, FileInfoPool]: ...
def hydrate_content(content: Content, pool: FileInfoPool) -> tuple[Content, FileInfoPool]: ...
```

### `kiarina.agi.data.display_content`

```python
from kiarina.agi.data.display_content import (
    BaseDisplayContent,
    DisplayContent,
    DisplayContentType,
    FileDisplayContent,
    TextDisplayContent,
)
```

### `kiarina.agi.data.embedding`

```python
from kiarina.agi.data.embedding import (
    Embedding,
    EmbeddingID,
    EmbeddingKind,
    EmbeddingSearchResult,
    EmbeddingSpace,
    EmbeddingSpaceID,
    EmbeddingVector,
    calc_cosine_similarity,
    l2_normalize,
    search_embeddings,
)

def calc_cosine_similarity(x: Embedding | np.ndarray, y: Embedding | np.ndarray) -> float: ...
def l2_normalize(vector: np.ndarray) -> EmbeddingVector: ...
def search_embeddings(
    query: Embedding | np.ndarray,
    candidates: Iterable[Embedding],
    *,
    top_k: int = 10,
    min_score: float | None = None,
) -> list[EmbeddingSearchResult]: ...
```

### `kiarina.agi.data.event`

```python
from kiarina.agi.data.event import (
    AIMessageChunkEvent,
    AIMessageEvent,
    BaseEvent,
    CustomEvent,
    Event,
    EventType,
    HumanMessageEvent,
    ToolMessageEvent,
    dehydrate_event,
    dehydrate_events,
    message_to_event,
)

def dehydrate_event(event: Event, pool: FileInfoPool) -> tuple[Event, FileInfoPool]: ...
def dehydrate_events(events: list[Event], pool: FileInfoPool) -> tuple[list[Event], FileInfoPool]: ...
def message_to_event(message: Message) -> Event: ...
```

### `kiarina.agi.data.file_bundle`

```python
from kiarina.agi.data.file_bundle import (
    FileBundle,
    FileBundleContent,
    FileBundleContentInput,
    FileBundleContentVisibility,
    FileBundleFilePath,
    FileBundleManifest,
    FileBundleMediaContent,
    FileBundleMediaContentSpec,
    FileBundleMediaContentType,
    FileBundleTextContent,
    FileBundleTextContentSpec,
)
```

### `kiarina.agi.data.file_info`

```python
from kiarina.agi.data.file_info import (
    AudioFileInfo,
    BaseFileInfo,
    FileID,
    FileInfo,
    FileType,
    Group,
    ImageFileInfo,
    OtherFileInfo,
    PDFFileInfo,
    TextFileInfo,
    UniqueKey,
    VideoFileInfo,
    deduplicate_file_infos,
    detect_file_type,
    shrink_file_infos,
)

def deduplicate_file_infos(file_infos: list[FileInfo]) -> list[FileInfo]: ...
def detect_file_type(file_blob: FileBlob) -> FileType: ...
def shrink_file_infos(
    file_infos: list[FileInfo],
    *,
    reduce: TokenCount,
    reserve: TokenCount = 0,
) -> tuple[list[FileInfo], TokenCount]: ...
```

### `kiarina.agi.data.file_info_pool`

```python
from kiarina.agi.data.file_info_pool import (
    FileInfoPool,
    dehydrate_file_infos,
    find_file_index,
    hydrate_file_infos,
)

def dehydrate_file_infos(file_infos: list[FileInfo], pool: FileInfoPool) -> tuple[list[FileInfo], FileInfoPool]: ...
def find_file_index(pool: FileInfoPool, file_id: FileID) -> int | None: ...
def hydrate_file_infos(file_infos: list[FileInfo], pool: FileInfoPool) -> tuple[list[FileInfo], FileInfoPool]: ...
```

### `kiarina.agi.data.history`

```python
from kiarina.agi.data.history import History
```

### `kiarina.agi.data.message`

```python
from kiarina.agi.data.message import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    Message,
    MessageType,
    SystemMessage,
    ToolCall,
    ToolCallChunk,
    ToolMessage,
    dehydrate_message,
    hydrate_messages,
)

def dehydrate_message(message: Message, pool: FileInfoPool) -> tuple[Message, FileInfoPool]: ...
def hydrate_messages(messages: list[Message], pool: FileInfoPool) -> tuple[list[Message], FileInfoPool]: ...
```

### `kiarina.agi.data.tool_info`

```python
from kiarina.agi.data.tool_info import (
    ToolChoice,
    ToolInfo,
    ToolName,
    ToolState,
    create_tool_info,
)

def create_tool_info(
    source: type[BaseModel] | dict[str, Any],
    name: ToolName | None = None,
    description: str | None = None,
    cache_control: dict[str, Any] | None = None,
) -> ToolInfo: ...
```
