# kiarina-agi-text

[English](README.md) | 日本語

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-text.svg)](https://pypi.org/project/kiarina-agi-text/)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-agi-text.svg)](https://pypi.org/project/kiarina-agi-text/)
[![License](https://img.shields.io/pypi/l/kiarina-agi-text.svg)](https://github.com/kiarina/kiarina-python/blob/main/LICENSE)

> [!NOTE] これは何？
> AI エージェント向けに、切り替え可能なチャットモデル、チャットログ、テキスト埋め込みを提供します。

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](https://pypi.org/project/kiarina-agi-base/) | `>=2.6.0` | MIT |
| [kiarina-agi-data](https://pypi.org/project/kiarina-agi-data/) | `>=2.6.0` | MIT |
| [kiarina-agi-file](https://pypi.org/project/kiarina-agi-file/) | `>=2.6.0` | MIT |
| [kiarina-utils-app](https://pypi.org/project/kiarina-utils-app/) | `>=2.4.0` | MIT |
| [kiarina-utils-common](https://pypi.org/project/kiarina-utils-common/) | `>=2.3.0` | MIT |
| [kiarina-utils-file](https://pypi.org/project/kiarina-utils-file/) | `>=2.3.1` | MIT |
| [LangChain](https://github.com/langchain-ai/langchain) | `>=1.0.0,<2` | MIT |
| [langchain-core](https://github.com/langchain-ai/langchain) | `>=1.0.0,<2` | MIT |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |

### Optional Dependencies

#### `chat-provider-lc-anthropic`

Anthropic API によるチャットに使用します。

| Package | Version | License |
| --- | --- | --- |
| [anthropic](https://github.com/anthropics/anthropic-sdk-python) | `>=0.84.0,<1` | [MIT](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE) |
| [langchain-anthropic](https://github.com/langchain-ai/langchain-anthropic) | `>=1.0.0,<2` | [MIT](https://github.com/langchain-ai/langchain-anthropic/blob/main/LICENSE) |

#### `chat-provider-lc-anthropic-vertex`

Vertex AI 上の Anthropic モデルによるチャットに使用します。

| Package | Version | License |
| --- | --- | --- |
| [anthropic](https://github.com/anthropics/anthropic-sdk-python) | `>=0.84.0,<1` | [MIT](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE) |
| [kiarina-lib-google](https://pypi.org/project/kiarina-lib-google/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [langchain-anthropic](https://github.com/langchain-ai/langchain-anthropic) | `>=1.0.0,<2` | [MIT](https://github.com/langchain-ai/langchain-anthropic/blob/main/LICENSE) |
| [langchain-google-vertexai](https://github.com/langchain-ai/langchain-google) | `>=3.0.0,<4` | [MIT](https://github.com/langchain-ai/langchain-google/blob/main/LICENSE) |

#### `chat-provider-lc-google-genai`

Gemini API または Vertex AI によるチャットに使用します。

| Package | Version | License |
| --- | --- | --- |
| [google-genai](https://github.com/googleapis/python-genai) | `>=1.65.0,<3` | [Apache-2.0](https://github.com/googleapis/python-genai/blob/main/LICENSE) |
| [kiarina-lib-google](https://pypi.org/project/kiarina-lib-google/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [langchain-google-genai](https://github.com/langchain-ai/langchain-google) | `>=4.0.0,<5` | [MIT](https://github.com/langchain-ai/langchain-google/blob/main/LICENSE) |

#### `chat-provider-lc-openai`

OpenAI API または OpenAI 互換 API によるチャットに使用します。

| Package | Version | License |
| --- | --- | --- |
| [kiarina-lib-openai](https://pypi.org/project/kiarina-lib-openai/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [langchain-openai](https://github.com/langchain-ai/langchain-openai) | `>=1.0.0,<2` | [MIT](https://github.com/langchain-ai/langchain-openai/blob/main/LICENSE) |
| [openai](https://github.com/openai/openai-python) | `>=2.0.1,<3` | [Apache-2.0](https://github.com/openai/openai-python/blob/main/LICENSE) |

#### `chat-provider-mock`

外部 API を使わないチャットに使用します。

| Package | Version | License |
| --- | --- | --- |
| [ulid-py](https://github.com/ahawker/ulid) | `>=1.1.0` | [Apache-2.0](https://github.com/ahawker/ulid/blob/master/LICENSE) |

#### `text-embedding-provider-google`

Gemini API または Vertex AI によるテキスト埋め込みに使用します。

| Package | Version | License |
| --- | --- | --- |
| [google-genai](https://github.com/googleapis/python-genai) | `>=1.65.0,<3` | [Apache-2.0](https://github.com/googleapis/python-genai/blob/main/LICENSE) |
| [kiarina-lib-google](https://pypi.org/project/kiarina-lib-google/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |

#### `text-embedding-provider-mock`

外部 API を使わないテキスト埋め込みに使用します。

| Package | Version | License |
| --- | --- | --- |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |

#### `text-embedding-provider-openai`

OpenAI API または OpenAI 互換 API によるテキスト埋め込みに使用します。

| Package | Version | License |
| --- | --- | --- |
| [kiarina-lib-openai](https://pypi.org/project/kiarina-lib-openai/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| [openai](https://github.com/openai/openai-python) | `>=2.0.1,<3` | [Apache-2.0](https://github.com/openai/openai-python/blob/main/LICENSE) |
| [tiktoken](https://github.com/openai/tiktoken) | `>=0.13.0` | [MIT](https://github.com/openai/tiktoken/blob/main/LICENSE) |

## Installation

基本パッケージと、使用する実装の Extra を導入します。

```bash
pip install kiarina-agi-text
pip install "kiarina-agi-text[chat-provider-lc-openai]"
```

複数の実装をまとめて導入できます。

```bash
pip install "kiarina-agi-text[chat-provider-lc-anthropic,chat-provider-lc-google-genai,text-embedding-provider-openai]"
```

## Features

- **Chat Models**
  名前または alias でモデルを選択し、単発応答またはストリームを取得します。
- **Provider Implementations**
  Anthropic、Google、OpenAI、mock の実装を同じインターフェースで使用します。
- **Chat Logging**
  チャットの開始、応答、ストリームを console または null logger に記録します。
- **Text Embeddings**
  登録済みモデルを選択し、同じ API でテキストをベクトル化します。

### Chat Models

`RunContext` はすべての呼び出しで必須です。mock provider を使う例では外部 API の認証情報は不要です。

```python
from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import HumanMessage
from kiarina.agi.run_context import RunContext

message = await invoke_chat(
    [HumanMessage.create("Hello")],
    chat_options={"chat_model": "mock"},
    run_context=RunContext(),
)
```

ストリームでは `AIMessageChunk` と、最後の `AIMessage` が順に返ります。

```python
from kiarina.agi.chat_model import stream_chat
from kiarina.agi.message import HumanMessage
from kiarina.agi.run_context import RunContext

async for item in stream_chat(
    [HumanMessage.create("Hello")],
    chat_options={"chat_model": "mock"},
    run_context=RunContext(),
):
    print(item.text, end="")
```

### Text Embeddings

```python
from kiarina.agi.run_context import RunContext
from kiarina.agi.text_embedding_model import embed_text

embedding = await embed_text(
    "Hello",
    text_embedding_options={"text_embedding_model": "mock"},
    run_context=RunContext(),
)
```

### Configuration

設定は `pydantic-settings-manager` で解決されます。既定モデル、alias、preset、custom implementation は各公開 `Settings` クラスで変更できます。

## API Reference

### `kiarina.agi.chat_model`

```python
from kiarina.agi.chat_model import (
    ChatModel,
    ChatModelAlias,
    ChatModelConfig,
    ChatModelName,
    ChatModelSettings,
    ChatModelSpecifier,
    ChatOptions,
    chat_model_registry,
    invoke_chat,
    run_chat,
    settings_manager,
    stream_chat,
)
```

```python
async def invoke_chat(
    messages: list[Message],
    *,
    tool_infos: list[ToolInfo] | None = None,
    chat_options: ChatOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> AIMessage: ...

async def run_chat(
    messages: list[Message],
    *,
    tool_infos: list[ToolInfo] | None = None,
    chat_options: ChatOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> AsyncIterator[AIMessageChunk | AIMessage]: ...

async def stream_chat(
    messages: list[Message],
    *,
    tool_infos: list[ToolInfo] | None = None,
    chat_options: ChatOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> AsyncIterator[AIMessageChunk | AIMessage]: ...

class ChatModel:
    def __init__(self, name: ChatModelName, config: ChatModelConfig) -> None: ...
    @property
    def provider_name(self) -> ChatProviderName: ...
    @property
    def provider_config(self) -> dict[str, Any]: ...
    @property
    def token_scale_factor(self) -> float: ...
    @property
    def provider(self) -> ChatProvider: ...
    def get_capabilities(self) -> ChatCapabilities: ...
    async def run(
        self,
        messages: list[Message],
        *,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> AsyncIterator[AIMessageChunk | AIMessage]: ...

class ChatModelConfig(BaseModel):
    provider_name: ChatProviderName
    provider_config: dict[str, Any] = {}
    token_scale_factor: float = 1.0
    visible: bool = True

class ChatOptions(TypedDict, total=False):
    chat_model: ChatModel | ChatModelSpecifier | None
    tool_choice: ToolChoice | None
    parallel_tool_calls: bool | None
    streaming: bool | None

ChatModelName: TypeAlias = str
ChatModelAlias: TypeAlias = str
ChatModelSpecifier: TypeAlias = ChatModelName | ChatModelAlias | str

chat_model_registry: ObjectRegistry[ChatModel, ChatModelConfig]
settings_manager: SettingsManager[ChatModelSettings]
```

`ChatModelSettings` は `default`、`aliases`、`presets`、`customs` を持つ Pydantic settings class です。

### `kiarina.agi.chat_provider`

```python
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProvider,
    ChatProviderContext,
    ChatProviderName,
    ChatProviderSettings,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
    chat_provider_registry,
    settings_manager,
)
```

```python
class ChatProvider(Protocol):
    name: ChatProviderName
    def get_capabilities(self) -> ChatCapabilities: ...
    def run(
        self,
        messages: list[Message],
        *,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> AsyncIterator[AIMessageChunk | AIMessage]: ...

class BaseChatProvider(ChatProvider):
    def __init__(self) -> None: ...
    name: ChatProviderName
    def get_capabilities(self) -> ChatCapabilities: ...
    async def run(
        self,
        messages: list[Message],
        *,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> AsyncIterator[AIMessageChunk | AIMessage]: ...

class ChatCapabilities(ChatLimits):
    input_enabled: dict[FileType, bool] = {}
    output_enabled: dict[FileType, bool] = {}
    def is_supported(self, file_type: FileType) -> bool: ...
    def can_include(self, message_type: MessageType, file_type: FileType) -> bool: ...
    def to_string(self) -> str: ...

@dataclass
class ChatProviderContext:
    messages: list[Message]
    tool_infos: list[ToolInfo] | None
    tool_choice: ToolChoice | None
    parallel_tool_calls: bool | None
    streaming: bool | None
    capabilities: ChatCapabilities
    cost_recorder: CostRecorder
    run_context: RunContext
    @classmethod
    def create(
        cls,
        *,
        messages: list[Message] | None = None,
        tool_infos: list[ToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        streaming: bool | None = None,
        capabilities: ChatCapabilities | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Self: ...

ChatProviderName: TypeAlias = str
chat_provider_registry: ComponentRegistry[ChatProvider]
settings_manager: SettingsManager[ChatProviderSettings]
```

`MaxTokenError`、`SafetyError`、`TokenOverflowError` は provider の失敗を表す例外です。`ChatProviderSettings` は `presets` と `customs` を持ちます。

### `kiarina.agi.chat_logger`

```python
from kiarina.agi.chat_logger import (
    BaseChatLogger,
    ChatLogger,
    ChatLoggerName,
    ChatLoggerSettings,
    ChatLoggerSpecifier,
    chat_logger_registry,
    settings_manager,
)
```

```python
class ChatLogger(Protocol):
    name: ChatLoggerName
    def log_chat_invoke_start(self, run_context: RunContext) -> None: ...
    def log_chat_invoke_end(
        self, ai_message: AIMessage, run_context: RunContext
    ) -> None: ...
    def log_chat_stream(
        self, run_context: RunContext
    ) -> AbstractContextManager[None]: ...
    def log_chat_stream_chunk(self, ai_message_chunk: AIMessageChunk) -> None: ...

class BaseChatLogger(ChatLogger):
    def __init__(self) -> None: ...
    name: ChatLoggerName
    def log_chat_invoke_start(self, run_context: RunContext) -> None: ...
    def log_chat_invoke_end(
        self, ai_message: AIMessage, run_context: RunContext
    ) -> None: ...
    def log_chat_stream(self, run_context: RunContext) -> Iterator[None]: ...
    def log_chat_stream_chunk(self, ai_message_chunk: AIMessageChunk) -> None: ...

ChatLoggerName: TypeAlias = str
ChatLoggerSpecifier: TypeAlias = ChatLoggerName | str
chat_logger_registry: ComponentRegistry[ChatLogger]
settings_manager: SettingsManager[ChatLoggerSettings]
```

`ChatLoggerSettings` は `default`、`presets`、`customs` を持ちます。

### `kiarina.agi.langchain_chat_provider`

```python
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProvider,
    LangChainChatProviderContext,
    LangChainMediaConverter,
    from_messages,
    from_tool_infos,
    has_content,
    normalize_content,
    remove_content,
    to_ai_message,
    to_ai_message_chunk,
)
```

```python
async def from_messages(
    messages: Sequence[Message],
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> list[LCMessage]: ...

def from_tool_infos(tool_infos: list[ToolInfo]) -> list[LCToolInfo]: ...
def to_ai_message(lc_ai_message: LCAIMessage) -> AIMessage: ...
def to_ai_message_chunk(lc_ai_message: LCAIMessageChunk) -> AIMessageChunk: ...
def has_content(lc_messages: list[LCMessage], content_type: str) -> bool: ...
def normalize_content(message: T) -> T: ...
def remove_content(message: T, content_type: str) -> T: ...

class LangChainMediaConverter:
    def to_image_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None: ...
    def to_audio_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None: ...
    def to_video_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None: ...
    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> dict[str, Any] | None: ...

class LangChainChatProvider(BaseChatProvider, LangChainMediaConverter, ABC):
    @property
    def request_logger(self) -> RequestLogger: ...

@dataclass
class LangChainChatProviderContext:
    lc_messages: list[LCMessage]
    lc_tool_infos: list[LCToolInfo] | None
    tool_choice: ToolChoice | None
    parallel_tool_calls: bool | None
    cost_recorder: CostRecorder
    run_context: RunContext
    def model_copy(self, **changes: Any) -> Self: ...
    @classmethod
    def create(
        cls,
        *,
        lc_messages: list[LCMessage] | None = None,
        lc_tool_infos: list[LCToolInfo] | None = None,
        tool_choice: ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Self: ...
```

`LCAIMessage`、`LCAIMessageChunk`、`LCBaseMessage`、`LCContent`、`LCHumanMessage`、`LCMessage`、`LCSystemMessage`、`LCToolCall`、`LCToolCallChunk`、`LCToolInfo`、`LCToolMessage` は LangChain の message、content、tool 型を表す公開型です。

### `kiarina.agi.text_embedding_model`

```python
from kiarina.agi.text_embedding_model import (
    TextEmbeddingModel,
    TextEmbeddingModelAlias,
    TextEmbeddingModelConfig,
    TextEmbeddingModelName,
    TextEmbeddingModelSettings,
    TextEmbeddingModelSpecifier,
    TextEmbeddingOptions,
    embed_text,
    settings_manager,
    text_embedding_model_registry,
)
```

```python
async def embed_text(
    text: str,
    *,
    text_embedding_options: TextEmbeddingOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
) -> Embedding: ...

class TextEmbeddingModel:
    def __init__(
        self, name: TextEmbeddingModelName, config: TextEmbeddingModelConfig
    ) -> None: ...
    @property
    def provider_name(self) -> TextEmbeddingProviderName: ...
    @property
    def provider_config(self) -> dict[str, Any]: ...
    @property
    def provider(self) -> TextEmbeddingProvider: ...
    def get_space(self) -> EmbeddingSpace: ...
    async def embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding: ...

class TextEmbeddingModelConfig(BaseModel):
    provider_name: TextEmbeddingProviderName
    provider_config: dict[str, Any] = {}
    visible: bool = True

class TextEmbeddingOptions(TypedDict, total=False):
    text_embedding_model: TextEmbeddingModel | TextEmbeddingModelSpecifier | None

TextEmbeddingModelName: TypeAlias = str
TextEmbeddingModelAlias: TypeAlias = str
TextEmbeddingModelSpecifier: TypeAlias = (
    TextEmbeddingModelName | TextEmbeddingModelAlias | str
)
text_embedding_model_registry: ObjectRegistry[
    TextEmbeddingModel, TextEmbeddingModelConfig
]
settings_manager: SettingsManager[TextEmbeddingModelSettings]
```

`TextEmbeddingModelSettings` は `default`、`aliases`、`presets`、`customs` を持ちます。

### `kiarina.agi.text_embedding_provider`

```python
from kiarina.agi.text_embedding_provider import (
    BaseTextEmbeddingProvider,
    TextEmbeddingProvider,
    TextEmbeddingProviderName,
    TextEmbeddingProviderSettings,
    settings_manager,
    text_embedding_provider_registry,
)
```

```python
class TextEmbeddingProvider(Protocol):
    name: TextEmbeddingProviderName
    def get_space(self) -> EmbeddingSpace: ...
    async def embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding: ...

class BaseTextEmbeddingProvider(TextEmbeddingProvider, ABC):
    def __init__(self) -> None: ...
    name: TextEmbeddingProviderName
    def get_space(self) -> EmbeddingSpace: ...
    async def embed(
        self,
        text: str,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> Embedding: ...

TextEmbeddingProviderName: TypeAlias = str
text_embedding_provider_registry: ComponentRegistry[TextEmbeddingProvider]
settings_manager: SettingsManager[TextEmbeddingProviderSettings]
```

`TextEmbeddingProviderSettings` は `presets` と `customs` を持ちます。

### Implementation Packages

各 factory は settings の field を `**kwargs` で上書きできます。各 settings class と `settings_manager` も同じ import path から公開されます。

```python
from kiarina.agi.chat_logger_impl.console import ConsoleChatLogger
from kiarina.agi.chat_logger_impl.null import NullChatLogger

class ConsoleChatLogger(BaseChatLogger):
    def __init__(self) -> None: ...

class NullChatLogger(BaseChatLogger):
    def __init__(self) -> None: ...
```

```python
def create_lc_anthropic_chat_provider(
    **kwargs: Any,
) -> LCAnthropicChatProvider: ...

def create_lc_anthropic_vertex_chat_provider(
    **kwargs: Any,
) -> LCAnthropicVertexChatProvider: ...

def create_lc_google_genai_chat_provider(
    **kwargs: Any,
) -> LCGoogleGenAIChatProvider: ...

def create_lc_openai_chat_provider(**kwargs: Any) -> LCOpenAIChatProvider: ...
def create_mock_chat_provider(**kwargs: Any) -> MockChatProvider: ...

class LCAnthropicChatProvider:
    def __init__(self, settings: LCAnthropicChatProviderSettings) -> None: ...

class LCAnthropicVertexChatProvider:
    def __init__(
        self, settings: LCAnthropicVertexChatProviderSettings
    ) -> None: ...

class LCGoogleGenAIChatProvider:
    def __init__(self, settings: LCGoogleGenAIChatProviderSettings) -> None: ...

class LCOpenAIChatProvider:
    def __init__(self, settings: LCOpenAIChatProviderSettings) -> None: ...

class MockChatProvider:
    def __init__(self, settings: MockChatProviderSettings) -> None: ...
```

`LCAnthropicChatProviderSettings`、`LCAnthropicVertexChatProviderSettings`、`LCGoogleGenAIChatProviderSettings`、`LCOpenAIChatProviderSettings`、`MockChatProviderSettings` と各 provider は、それぞれ次の公開 import path から import します。

- `kiarina.agi.chat_provider_impl.lc_anthropic`
- `kiarina.agi.chat_provider_impl.lc_anthropic_vertex`
- `kiarina.agi.chat_provider_impl.lc_google_genai`
- `kiarina.agi.chat_provider_impl.lc_openai`
- `kiarina.agi.chat_provider_impl.mock`

```python
def create_google_text_embedding_provider(
    **kwargs: Any,
) -> GoogleTextEmbeddingProvider: ...

def create_mock_text_embedding_provider(
    **kwargs: Any,
) -> MockTextEmbeddingProvider: ...

def create_openai_text_embedding_provider(
    **kwargs: Any,
) -> OpenAITextEmbeddingProvider: ...

class GoogleTextEmbeddingProvider:
    def __init__(
        self, settings: GoogleTextEmbeddingProviderSettings
    ) -> None: ...

class MockTextEmbeddingProvider:
    def __init__(self, settings: MockTextEmbeddingProviderSettings) -> None: ...

class OpenAITextEmbeddingProvider:
    def __init__(
        self, settings: OpenAITextEmbeddingProviderSettings
    ) -> None: ...
```

`GoogleTextEmbeddingProviderSettings`、`MockTextEmbeddingProviderSettings`、`OpenAITextEmbeddingProviderSettings` と各 provider は、それぞれ次の公開 import path から import します。

- `kiarina.agi.text_embedding_provider_impl.google`
- `kiarina.agi.text_embedding_provider_impl.mock`
- `kiarina.agi.text_embedding_provider_impl.openai`
