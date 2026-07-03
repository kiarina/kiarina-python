# kiarina-agi-data

[English](README.md) | 日本語

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-data.svg)](https://pypi.org/project/kiarina-agi-data/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] これは何？
> `kiarina-agi-data` は、AI agent の message、event、file、embedding、tool を一貫して扱うための型付き data model と変換 utility を提供します。

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

- **Message と event**
  system、human、AI、tool の message と streaming chunk を、時系列の event として管理します。
- **Content と file metadata**
  text と file をまとめて表現し、token 見積もり、XML 変換、縮小、共有 pool への退避と復元を行います。
- **History**
  event、file、tool、embedding を一つの状態として保持し、用途別に検索・更新します。
- **Embedding**
  vector の正規化、cosine similarity の計算、上位候補の検索を行います。
- **File bundle**
  text と media を manifest 付き ZIP にまとめ、byte 列や MIME blob と相互変換します。
- **Tool schema**
  Pydantic model または JSON Schema から tool 定義を作成し、実行状態を管理します。

### Build a Conversation History

`History` に追加した message は event に変換されます。message 内の file metadata は共有 pool に退避され、重複を避けて保持されます。

```python
from kiarina.agi.history import History
from kiarina.agi.message import AIMessage, HumanMessage

history = History()
history.add_message(HumanMessage.create("東京の天気を教えてください。"))
history.add_message(AIMessage.create("晴れの予報です。"))

messages = history.get_messages()
assert len(messages) == 2
assert messages[-1].to_text() == "晴れの予報です。"
```

### Search Embeddings

`search_embeddings` は cosine similarity の降順で結果を返します。

```python
import numpy as np

from kiarina.agi.embedding import Embedding, search_embeddings

candidates = [
    Embedding(kind="document", space_id="example", vector=[1.0, 0.0]),
    Embedding(kind="document", space_id="example", vector=[0.0, 1.0]),
]

results = search_embeddings(np.array([0.9, 0.1]), candidates, top_k=1)
assert results[0].embedding == candidates[0]
```

### Create a File Bundle

```python
from kiarina.agi.file_bundle import FileBundle

bundle = FileBundle.create(
    [
        {"type": "text", "text": "Summary"},
        {
            "type": "image",
            "file_path": "images/chart.png",
            "mime_type": "image/png",
        },
    ],
    files={"images/chart.png": b"PNG data"},
)

restored = FileBundle.from_bytes(bundle.to_bytes())
assert restored.files["images/chart.png"] == b"PNG data"
```

## API Reference

Pydantic model の constructor は、記載した field を keyword argument として受け取ります。`Field(default_factory=...)` の field は省略できます。

### `kiarina.agi.chat_estimates`

```python
from kiarina.agi.chat_estimates import ChatEstimates

class ChatEstimates:
    token_count: int = 0
    file_size: int = 0
    text_file_count: int = 0
    text_token_count: int = 0
    image_file_count: int = 0
    image_token_count: int = 0
    audio_duration: float = 0.0
    audio_file_count: int = 0
    audio_token_count: int = 0
    video_duration: float = 0.0
    video_file_count: int = 0
    video_token_count: int = 0
    pdf_page_count: int = 0
    pdf_file_count: int = 0
    pdf_token_count: int = 0

    @property
    def summary(self) -> str: ...
    @property
    def text(self) -> str: ...
    @property
    def image(self) -> str: ...
    @property
    def audio(self) -> str: ...
    @property
    def video(self) -> str: ...
    @property
    def pdf(self) -> str: ...
    def add_token_count(
        self,
        target: Literal["text", "image", "audio", "video", "pdf"],
        token_count: int,
    ) -> None: ...
    def to_string(self) -> str: ...
```

### `kiarina.agi.chat_limits`

```python
from kiarina.agi.chat_limits import ChatLimits, ChatLimitsSpecifier

ChatLimitsSpecifier: TypeAlias = str

class ChatLimits:
    token_count_limit: int = 772_000
    file_size_limit: int = 20_000_000
    image_file_count_limit: int = 100
    audio_duration_limit: float = 34_200.0
    audio_file_count_limit: int = 7
    video_duration_limit: float = 3_600.0
    video_file_count_limit: int = 7
    pdf_page_count_limit: int = 100
    pdf_file_count_limit: int = 7

    @property
    def token_count(self) -> str: ...
    @property
    def file_size(self) -> str: ...
    @property
    def image(self) -> str: ...
    @property
    def audio(self) -> str: ...
    @property
    def video(self) -> str: ...
    @property
    def pdf(self) -> str: ...
    def to_string(self) -> str: ...
    @classmethod
    def from_specifier(cls, specifier: ChatLimitsSpecifier) -> Self: ...
```

### `kiarina.agi.content`

```python
from kiarina.agi.content import Content, dehydrate_content, hydrate_content

def dehydrate_content(
    content: Content,
    pool: FileInfoPool,
) -> tuple[Content, FileInfoPool]: ...

def hydrate_content(
    content: Content,
    pool: FileInfoPool,
) -> tuple[Content, FileInfoPool]: ...

class Content:
    payload: dict[str, Any] | None = None
    text: str = ""
    files: list[FileInfo] = []
    cache_control: dict[str, Any] | None = None
    tag: str = "files"
    description: str = ""
    template: str = "<{tag}{attributes}>\n{inner_xml}\n</{tag}>"
    file_tags: dict[FileType, str] = {}

    @property
    def xml_attributes(self) -> dict[str, Any]: ...
    def to_estimates(self) -> ChatEstimates: ...
    def to_xml(self, inner_xml: str | None = None) -> str: ...
    def to_text(self) -> str: ...
```

### `kiarina.agi.display_content`

```python
from kiarina.agi.display_content import (
    BaseDisplayContent,
    DisplayContent,
    DisplayContentType,
    FileDisplayContent,
    TextDisplayContent,
)

DisplayContentType = Literal["text", "file"]
DisplayContent: TypeAlias = TextDisplayContent | FileDisplayContent

class BaseDisplayContent:
    type: DisplayContentType
    mime_type: str

class FileDisplayContent(BaseDisplayContent):
    type: Literal["file"] = "file"
    mime_type: str = "application/octet-stream"
    uri_or_file_path: str
    display_name: str | None = None

    @property
    def uri(self) -> str: ...

class TextDisplayContent(BaseDisplayContent):
    type: Literal["text"] = "text"
    mime_type: str = "text/plain"
    text: str
    start_line: int = 1
```

### `kiarina.agi.embedding`

```python
from kiarina.agi.embedding import (
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

EmbeddingID: TypeAlias = str
EmbeddingKind: TypeAlias = str
EmbeddingSpaceID: TypeAlias = str
EmbeddingVector: TypeAlias = Float32[np.ndarray, "dimensions"]

def calc_cosine_similarity(
    x: Embedding | np.ndarray,
    y: Embedding | np.ndarray,
) -> float: ...
def l2_normalize(vector: np.ndarray) -> EmbeddingVector: ...
def search_embeddings(
    query: Embedding | np.ndarray,
    candidates: Iterable[Embedding],
    *,
    top_k: int = 10,
    min_score: float | None = None,
) -> list[EmbeddingSearchResult]: ...

class Embedding:
    id: EmbeddingID = <generated ULID>
    created_at: datetime = <current UTC time>
    kind: EmbeddingKind
    space_id: EmbeddingSpaceID
    vector: list[float]
    metadata: dict[str, Any] = {}

    def to_numpy(self) -> EmbeddingVector: ...
    @classmethod
    def from_numpy(
        cls,
        *,
        kind: EmbeddingKind,
        space_id: EmbeddingSpaceID,
        vector: EmbeddingVector,
        metadata: dict[str, Any] | None = None,
    ) -> Self: ...

class EmbeddingSpace:
    kind: EmbeddingKind
    space_id: EmbeddingSpaceID
    dimension: int
    metadata: dict[str, Any] = {}

class EmbeddingSearchResult:
    embedding: Embedding
    score: float
```

### `kiarina.agi.event`

```python
from kiarina.agi.event import (
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

EventType = Literal[
    "human_message", "ai_message", "ai_message_chunk", "tool_message", "custom"
]
Event: TypeAlias = (
    HumanMessageEvent
    | AIMessageEvent
    | AIMessageChunkEvent
    | ToolMessageEvent
    | CustomEvent
)

def dehydrate_event(
    event: Event,
    pool: FileInfoPool,
) -> tuple[Event, FileInfoPool]: ...
def dehydrate_events(
    events: list[Event],
    pool: FileInfoPool,
) -> tuple[list[Event], FileInfoPool]: ...
def message_to_event(message: Message) -> Event: ...

class BaseEvent:
    type: EventType
    id: str = <generated ULID>
    created_at: datetime = <current UTC time>
    transient: bool = False
    hidden: bool = False

    def to_text(self) -> str: ...

class AIMessageChunkEvent(BaseEvent):
    type: Literal["ai_message_chunk"] = "ai_message_chunk"
    transient: bool = True
    message: AIMessageChunk

class AIMessageEvent(BaseEvent):
    type: Literal["ai_message"] = "ai_message"
    message: AIMessage

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        tool_calls: list[ToolCall] | None = None,
    ) -> Self: ...

class HumanMessageEvent(BaseEvent):
    type: Literal["human_message"] = "human_message"
    message: HumanMessage

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
    ) -> Self: ...

class ToolMessageEvent(BaseEvent):
    type: Literal["tool_message"] = "tool_message"
    message: ToolMessage

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        *,
        tool_name: str,
        tool_call_args: dict[str, Any] | None = None,
        tool_call_id: str,
    ) -> Self: ...

class CustomEvent(BaseEvent):
    type: Literal["custom"] = "custom"
    payload: dict[str, Any] = {}

    @classmethod
    def create(cls, **kwargs: Any) -> Self: ...
```

すべての具象 event class は `to_text(self) -> str` を実装します。

### `kiarina.agi.file_bundle`

```python
from kiarina.agi.file_bundle import (
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

FileBundleContentVisibility = Literal["always", "supported", "unsupported"]
FileBundleFilePath: TypeAlias = str
FileBundleMediaContentType = Literal["image", "audio", "video", "pdf"]
FileBundleContent: TypeAlias = FileBundleMediaContent | FileBundleTextContent
FileBundleContentInput: TypeAlias = (
    str
    | FileBundleTextContentSpec
    | FileBundleMediaContentSpec
    | FileBundleContent
)

class FileBundleTextContentSpec(TypedDict):
    type: Literal["text"]
    text: str
    visibility: NotRequired[FileBundleContentVisibility]

class FileBundleMediaContentSpec(TypedDict):
    type: FileBundleMediaContentType
    file_path: FileBundleFilePath
    mime_type: str
    visibility: NotRequired[FileBundleContentVisibility]

class FileBundleTextContent:
    type: Literal["text"] = "text"
    text: str
    visibility: FileBundleContentVisibility = "always"

class FileBundleMediaContent:
    type: FileBundleMediaContentType
    file_path: FileBundleFilePath
    mime_type: str
    visibility: FileBundleContentVisibility = "always"

class FileBundleManifest:
    FILE_NAME: ClassVar[str] = "manifest.json"
    contents: list[FileBundleContent] = []

    @classmethod
    def create(
        cls,
        contents: list[FileBundleContentInput],
    ) -> Self: ...

@dataclass
class FileBundle:
    manifest: FileBundleManifest = FileBundleManifest()
    files: dict[FileBundleFilePath, bytes] = {}
    MIME_TYPE: ClassVar[str] = "application/zip"

    def to_bytes(self) -> bytes: ...
    def to_mime_blob(self) -> MIMEBlob: ...
    @classmethod
    def from_bytes(cls, data: bytes) -> Self: ...
    @classmethod
    def from_mime_blob(cls, blob: MIMEBlob) -> Self: ...
    @classmethod
    def create(
        cls,
        manifest_contents: list[FileBundleContentInput],
        files: dict[FileBundleFilePath, bytes] | None = None,
    ) -> Self: ...
```

`FileBundle` は `+` で結合できます。同じ file path を含む bundle、manifest が参照する file を欠く bundle、安全でない ZIP path は `ValueError` になります。

### `kiarina.agi.file_info`

```python
from kiarina.agi.file_info import (
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

FileID: TypeAlias = str
Group: TypeAlias = str
UniqueKey: TypeAlias = str
FileType = Literal["text", "image", "audio", "video", "pdf", "other"]
FileInfo: TypeAlias = (
    TextFileInfo
    | ImageFileInfo
    | AudioFileInfo
    | VideoFileInfo
    | PDFFileInfo
    | OtherFileInfo
)

def deduplicate_file_infos(file_infos: list[FileInfo]) -> list[FileInfo]: ...
def detect_file_type(file_blob: FileBlob) -> FileType: ...
def shrink_file_infos(
    file_infos: list[FileInfo],
    *,
    reduce: TokenCount,
    reserve: TokenCount = 0,
) -> tuple[list[FileInfo], TokenCount]: ...

class BaseFileInfo:
    type: FileType
    id: FileID = <generated ULID>
    created_at: datetime = <current UTC time>
    node_id: str = <current node ID>
    mime_type: str
    file_hash: str
    file_size: int
    token_count: TokenCount
    intermediate_file_path: str | None
    asset_uri: str | None
    uri_or_file_path: URIOrFilePath
    name: str = ""
    description: str = ""
    pinned: bool = False
    inline: bool = False
    metadata_only: bool = False
    content_only: bool = False
    no_merge: bool = False
    group: Group | None = None
    unique_key: UniqueKey | None = None
    keep_from_end: bool = False
    tag: str = "file"
    default_template: str = "<{tag}{attributes} />"
    metadata_only_template: str = '<{tag}{attributes} metadata_only="True" />'

    @property
    def is_uri(self) -> bool: ...
    @property
    def uri(self) -> str: ...
    @property
    def prepared(self) -> bool: ...
    @property
    def xml_attributes(self) -> dict[str, Any]: ...
    @property
    def optional_export_fields(self) -> tuple[str, ...]: ...
    def export(self) -> dict[str, Any]: ...
    def to_estimates(self) -> ChatEstimates: ...
    def to_metadata_estimates(self) -> ChatEstimates: ...
    def to_content_estimates(self) -> ChatEstimates: ...
    def to_xml(self, tag: str | None = None) -> str: ...
    def to_metadata_only_xml(self, tag: str | None = None) -> str: ...
    def as_metadata_only(self) -> Self: ...
    def shrink(
        self,
        reduce: TokenCount,
        reserve: TokenCount = 0,
    ) -> tuple[Self, TokenCount]: ...
    def get_value(self, field_name: str, default: Any = None) -> Any: ...
```

具象 class は次の固有 field と property を追加します。

```python
class TextFileInfo(BaseFileInfo):
    type: Literal["text"] = "text"
    start_line: int = 1
    end_line: int = -1
    line_count: int
    raw_text: str | None

    @property
    def normalized_start_line(self) -> int: ...
    @property
    def normalized_end_line(self) -> int: ...
    @property
    def segment_line_count(self) -> int: ...
    def shrink_by_line(self, keep_line_count: int) -> Self: ...

class ImageFileInfo(BaseFileInfo):
    type: Literal["image"] = "image"
    width: int
    height: int

class AudioFileInfo(BaseFileInfo):
    type: Literal["audio"] = "audio"
    start_time: float = 0.0
    end_time: float = -1.0
    duration: float

    @property
    def normalized_start_time(self) -> float: ...
    @property
    def normalized_end_time(self) -> float: ...
    @property
    def segment_duration(self) -> float: ...

class VideoFileInfo(AudioFileInfo):
    type: Literal["video"] = "video"
    width: int
    height: int

class PDFFileInfo(BaseFileInfo):
    type: Literal["pdf"] = "pdf"
    start_page: int = 1
    end_page: int = -1
    page_count: int

    @property
    def normalized_start_page(self) -> int: ...
    @property
    def normalized_end_page(self) -> int: ...
    @property
    def segment_page_count(self) -> int: ...

class OtherFileInfo(BaseFileInfo):
    type: Literal["other"] = "other"
```

具象 class は content 種別に応じた `xml_attributes`、`optional_export_fields`、`to_content_estimates()` も実装します。

### `kiarina.agi.file_info_pool`

```python
from kiarina.agi.file_info_pool import (
    FileInfoPool,
    dehydrate_file_infos,
    find_file_index,
    hydrate_file_infos,
)

FileInfoPool: TypeAlias = list[FileInfo]

def dehydrate_file_infos(
    file_infos: list[FileInfo],
    pool: FileInfoPool,
) -> tuple[list[FileInfo], FileInfoPool]: ...
def find_file_index(pool: FileInfoPool, file_id: FileID) -> int | None: ...
def hydrate_file_infos(
    file_infos: list[FileInfo],
    pool: FileInfoPool,
) -> tuple[list[FileInfo], FileInfoPool]: ...
```

### `kiarina.agi.history`

```python
from kiarina.agi.history import History

class History:
    events: list[Event] = []
    file_infos: FileInfoPool = []
    tool_infos: list[ToolInfo] = []
    embeddings: dict[EmbeddingID, Embedding] = {}
    metadata: dict[str, Any] = {}

    def clear(self) -> None: ...
    def get_last_event(self, event_type: EventType) -> Event | None: ...
    def get_pending_tool_calls(self) -> list[ToolCall]: ...
    def add_event(self, event: Event) -> None: ...
    def replace_event(self, target: Event, replacement: Event) -> None: ...
    def get_last_message(self, message_type: MessageType) -> Message | None: ...
    def get_messages(self) -> list[Message]: ...
    def add_message(self, message: Message) -> None: ...
    def get_file_info(self, *, unique_key: UniqueKey) -> FileInfo | None: ...
    def get_file_infos(
        self,
        *,
        uri_or_file_path: URIOrFilePath | None = None,
        group: Group | None = None,
        no_group: bool = False,
        no_unique_key: bool = False,
        ignore_unique_keys: list[UniqueKey] | None = None,
        in_message: bool | None = None,
    ) -> list[FileInfo]: ...
    def add_file_info(self, file_info: FileInfo) -> None: ...
    def remove_file_info(self, file_id: FileID) -> None: ...
    def get_tool_info(self, name: ToolName) -> ToolInfo | None: ...
    def get_tool_infos(
        self,
        *,
        state: ToolState | None = None,
    ) -> list[ToolInfo]: ...
    def add_tool_info(self, tool_info: ToolInfo) -> None: ...
    def remove_tool_info(self, name: ToolName) -> None: ...
    def get_embedding(self, embedding_id: EmbeddingID) -> Embedding | None: ...
    def add_embedding(self, embedding: Embedding) -> None: ...
    def remove_embedding(self, embedding_id: EmbeddingID) -> None: ...
    def get_embeddings(
        self,
        *,
        kind: EmbeddingKind | None = None,
        space_id: EmbeddingSpaceID | None = None,
    ) -> list[Embedding]: ...
```

### `kiarina.agi.message`

```python
from kiarina.agi.message import (
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

MessageType = Literal["system", "human", "ai", "ai_chunk", "tool"]
Message: TypeAlias = (
    SystemMessage | HumanMessage | AIMessage | AIMessageChunk | ToolMessage
)

def dehydrate_message(
    message: Message,
    pool: FileInfoPool,
) -> tuple[Message, FileInfoPool]: ...
def hydrate_messages(
    messages: list[Message],
    pool: FileInfoPool,
) -> tuple[list[Message], FileInfoPool]: ...

class BaseMessage:
    type: MessageType
    contents: list[Content] = []

    def get_file_infos(self) -> list[FileInfo]: ...
    def contents_to_text(self) -> str: ...
    def to_estimates(self) -> ChatEstimates: ...
    def to_text(self) -> str: ...
    def replace_content(self, old: Content, new: Content) -> Self: ...
    def shrink(
        self,
        pool: FileInfoPool,
        reduce: TokenCount,
        reserve: TokenCount = 0,
    ) -> tuple[FileInfoPool, TokenCount]: ...

class SystemMessage(BaseMessage):
    type: Literal["system"] = "system"
    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
    ) -> Self: ...

class HumanMessage(BaseMessage):
    type: Literal["human"] = "human"
    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
    ) -> Self: ...

class AIMessage(BaseMessage):
    type: Literal["ai"] = "ai"
    tool_calls: list[ToolCall] = []
    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        *,
        tool_calls: list[ToolCall] | None = None,
    ) -> Self: ...

class AIMessageChunk(AIMessage):
    type: Literal["ai_chunk"] = "ai_chunk"
    tool_call_chunks: list[ToolCallChunk] = []

class ToolMessage(BaseMessage):
    type: Literal["tool"] = "tool"
    tool_name: str
    tool_call_args: dict[str, Any] = {}
    tool_call_id: str
    return_direct: bool = False
    failed: bool = False
    artifact: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
    display_contents: list[DisplayContent] = []

    @classmethod
    def create(
        cls,
        text: str = "",
        files: list[FileInfo] | None = None,
        *,
        tool_name: str,
        tool_call_args: dict[str, Any] | None = None,
        tool_call_id: str,
    ) -> Self: ...

class ToolCall:
    id: str = <generated ULID>
    name: str
    args: dict[str, Any] = {}

    def to_estimates(self) -> ChatEstimates: ...
    def to_text(self) -> str: ...

class ToolCallChunk:
    id: str | None = None
    name: str | None = None
    args: str | None = None
    index: int | None = None
```

### `kiarina.agi.tool_info`

```python
from kiarina.agi.tool_info import (
    ToolChoice,
    ToolInfo,
    ToolName,
    ToolState,
    create_tool_info,
)

ToolName: TypeAlias = str
ToolChoice: TypeAlias = Literal["auto", "any"] | ToolName
ToolState = Literal["active", "inactive", "disabled"]

def create_tool_info(
    source: type[BaseModel] | dict[str, Any],
    name: ToolName | None = None,
    description: str | None = None,
    cache_control: dict[str, Any] | None = None,
) -> ToolInfo: ...

class ToolInfo:
    name: ToolName
    description: str
    args_schema: dict[str, Any] = {}
    cache_control: dict[str, Any] | None = None
    state: ToolState = "active"

    def to_estimates(self) -> ChatEstimates: ...
    def to_json_schema(self) -> dict[str, Any]: ...
```
