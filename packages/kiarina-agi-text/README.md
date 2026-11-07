# kiarina-agi-text

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-text.svg)](https://pypi.org/project/kiarina-agi-text/)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-agi-text.svg)](https://pypi.org/project/kiarina-agi-text/)
[![License](https://img.shields.io/pypi/l/kiarina-agi-text.svg)](https://github.com/kiarina/kiarina-python/blob/main/LICENSE)

> [!NOTE] What is this?
> Provides interchangeable chat models, chat logging, and text embeddings for AI agents.

## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](https://pypi.org/project/kiarina-agi-base/) | `>=2.6.0` | MIT |
| [kiarina-agi-data](https://pypi.org/project/kiarina-agi-data/) | `>=2.36.0` | MIT |
| [kiarina-agi-file](https://pypi.org/project/kiarina-agi-file/) | `>=2.6.0` | MIT |
| [kiarina-utils-app](https://pypi.org/project/kiarina-utils-app/) | `>=2.4.0` | MIT |
| [kiarina-utils-common](https://pypi.org/project/kiarina-utils-common/) | `>=2.3.0` | MIT |
| [kiarina-utils-file](https://pypi.org/project/kiarina-utils-file/) | `>=2.3.1` | MIT |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |

### Optional Dependencies

| Package | Version | License | Extras |
| --- | --- | --- | --- |
| [anthropic](https://github.com/anthropics/anthropic-sdk-python) | `>=0.84.0,<2` | [MIT](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE) | `chat-provider-anthropic`<br>`chat-provider-anthropic-vertex` |
| [claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk-python) | `>=0.2.164` | [MIT](https://github.com/anthropics/claude-agent-sdk-python/blob/main/LICENSE) | `chat-provider-claude-code` |
| [FastAPI](https://github.com/fastapi/fastapi) | `>=0.162.0,<1` | [MIT](https://github.com/fastapi/fastapi/blob/master/LICENSE) | `chat-proxy` |
| [google-genai](https://github.com/googleapis/python-genai) | `>=1.65.0,<3` | [Apache-2.0](https://github.com/googleapis/python-genai/blob/main/LICENSE) | `chat-provider-google`<br>`text-embedding-provider-google` |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1,<1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) | `chat-provider-proxy` |
| [kiarina-lib-anthropic](https://pypi.org/project/kiarina-lib-anthropic/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) | `chat-provider-anthropic`<br>`chat-provider-anthropic-vertex` |
| [kiarina-lib-google](https://pypi.org/project/kiarina-lib-google/) | `>=2.4.0` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) | `chat-provider-anthropic-vertex`<br>`chat-provider-google`<br>`text-embedding-provider-google` |
| [kiarina-lib-openai](https://pypi.org/project/kiarina-lib-openai/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) | `chat-provider-openai`<br>`text-embedding-provider-openai` |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) | `text-embedding-provider-google`<br>`text-embedding-provider-mock`<br>`text-embedding-provider-openai` |
| [openai](https://github.com/openai/openai-python) | `>=2.0.1,<4` | [Apache-2.0](https://github.com/openai/openai-python/blob/main/LICENSE) | `chat-provider-openai`<br>`text-embedding-provider-openai` |
| [openai-codex-cli-bin](https://github.com/openai/codex) | `>=0.160.1` | [Apache-2.0](https://github.com/openai/codex/blob/main/LICENSE) | `chat-provider-codex` |
| [tiktoken](https://github.com/openai/tiktoken) | `>=0.13.0` | [MIT](https://github.com/openai/tiktoken/blob/main/LICENSE) | `text-embedding-provider-openai` |
| [ulid-py](https://github.com/ahawker/ulid) | `>=1.1.0` | [Apache-2.0](https://github.com/ahawker/ulid/blob/master/LICENSE) | `chat-provider-mock` |
| [Uvicorn](https://github.com/encode/uvicorn) | `>=0.54.0,<1` | [BSD-3-Clause](https://github.com/encode/uvicorn/blob/master/LICENSE.md) | `chat-proxy` |

The `all` Extra installs every optional dependency listed above except those of `chat-proxy`, so apps that use chat models do not get a web server.

## Installation

```bash
pip install "kiarina-agi-text[all]"
```

## Features

- **Chat Models**
  Select a model by name or alias and receive one response or a stream. Tool calls and image, audio, video, and PDF inputs and outputs are also supported.
- **Chat Proxy**
  Run chat models on another machine over HTTP: the chat proxy serves its chat models, and the `proxy` chat provider calls them. For example, a container can use `codex` and `claude_code` with the host's subscription logins without having them itself.
- **Text Embeddings**
  Select a registered model and vectorize text through one API.

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

`ChatModelSettings` is a Pydantic settings class with `default`, `aliases`, `presets`, and `customs` fields.

### `kiarina.agi.chat_proxy`

```python
from kiarina.agi.chat_proxy import (
    ChatProxyError,
    ChatProxyErrorInfo,
    ChatProxyEvent,
    ChatProxyFile,
    ChatProxyMissingFilesError,
    ChatProxyModelInfo,
    ChatProxyRequest,
    ChatProxySettings,
    attach_chat_proxy_files,
    collect_chat_proxy_files,
    create_chat_proxy_app,
    expire_chat_proxy_cache,
    find_missing_chat_proxy_files,
    run_chat_proxy,
    settings_manager,
)
```

```python
def create_chat_proxy_app(settings: ChatProxySettings | None = None) -> FastAPI: ...

def run_chat_proxy(settings: ChatProxySettings | None = None) -> None: ...

async def collect_chat_proxy_files(
    messages: list[Message],
    *,
    run_context: RunContext,
    known_hashes: Container[str] = (),
) -> dict[str, ChatProxyFile]: ...

async def find_missing_chat_proxy_files(
    sha256s: list[str], *, run_context: RunContext
) -> list[str]: ...

def expire_chat_proxy_cache(
    cache_dir: str | os.PathLike[str], ttl: int, *, now: float | None = None
) -> int: ...

async def attach_chat_proxy_files(
    messages: list[Message],
    files: dict[str, ChatProxyFile],
    *,
    run_context: RunContext,
) -> list[Message]: ...

class ChatProxySettings(BaseSettings):  # env prefix: KIARINA_AGI_CHAT_PROXY_
    host: str = "127.0.0.1"
    port: int = 8795
    token: SecretStr | None = None
    allowed_models: list[str] | None = None
    max_concurrency: int = 4
    cache_ttl: int = 86400

class ChatProxyRequest(BaseModel):
    model_name: str
    messages: list[Message]
    tool_infos: list[ToolInfo] | None = None
    tool_choice: ToolChoice | None = None
    parallel_tool_calls: bool | None = None
    streaming: bool | None = None
    run_context: RunContext
    files: dict[str, ChatProxyFile] = {}

class ChatProxyFile(BaseModel):
    mime_type: str
    sha256: str
    base64_data: str | None = None

class ChatProxyEvent(BaseModel):
    type: Literal["chunk", "message", "cost", "error"]
    message: AIMessageChunk | AIMessage | None = None
    cost_record: CostRecord | None = None
    error: ChatProxyErrorInfo | None = None

class ChatProxyErrorInfo(BaseModel):
    kind: Literal["safety", "max_token", "token_overflow", "other"]
    error_type: str
    message: str
    category: str | None = None
    request_id: str | None = None
    token_count: int | None = None
    limit: int | None = None
    @classmethod
    def from_exception(cls, error: BaseException) -> Self: ...
    def to_exception(self) -> Exception: ...

class ChatProxyModelInfo(BaseModel):
    name: str
    capabilities: ChatCapabilities

class ChatProxyError(Exception): ...

class ChatProxyMissingFilesError(ChatProxyError):
    hashes: list[str]

settings_manager: SettingsManager[ChatProxySettings]
```

The chat proxy serves two endpoints, both requiring `Authorization: Bearer <token>` when `token` is set:

| Endpoint | Response |
| --- | --- |
| `GET /v1/chat-models/{model_name}` | `ChatProxyModelInfo` |
| `POST /v1/files/missing` with a `ChatProxyMissingFilesRequest` | `ChatProxyMissingFiles`: the hashes the proxy does not have |
| `POST /v1/chat` with a `ChatProxyRequest` | NDJSON lines of `ChatProxyEvent`: chunks, the final message, then cost records, or an error. `409` with `{"missing": [<sha256>, ...]}` when a file sent without contents is not on the proxy |

The proxy keeps the files it receives in the app's user cache directory and deletes every file there not used for `cache_ttl` seconds (one day by default; `0` keeps them), at startup and hourly. Using a file, in a chat request or a `/v1/files/missing` check, touches it. A caller sends a deleted file again on its next request.

Run it with the `kiarina-chat-proxy` command (`pip install "kiarina-agi-text[chat-proxy]"` plus the extras of the chat providers it serves). Callers use the `proxy` chat provider (`pip install "kiarina-agi-text[chat-provider-proxy]"`):

```python
ChatModelConfig(
    provider_name="proxy",
    provider_config={
        "base_url": "http://host.docker.internal:8795",
        "model_name": "codex",
        "token": "...",
    },
)
```

`ProxyChatProviderSettings` (env prefix `KIARINA_AGI_CHAT_PROVIDER_IMPL_PROXY_`) has `base_url`, `model_name`, `token`, and `timeout`. The provider reads the chat model's capabilities from the proxy once. Media files are read where the caller runs and sent with their SHA-256; the proxy stores them in its asset repository under that hash. Before a request with files, the provider asks the proxy which hashes it lacks and sends contents only for those; it remembers nothing itself, so the proxy may purge its copies at any time. A `409` from the chat request (the proxy lost a file after the check) raises `ChatProxyError`. A media file the caller cannot read is sent as metadata only. Chat provider errors (`SafetyError`, `MaxTokenError`, `TokenOverflowError`) are raised again on the caller with their fields; other errors become `ChatProxyError`.

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

`TextEmbeddingModelSettings` has `default`, `aliases`, `presets`, and `customs` fields.
