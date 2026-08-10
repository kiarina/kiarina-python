# kiarina-agi-text

English | [日本語](README.ja.md)

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

| Package | Version | License | Extras |
| --- | --- | --- | --- |
| [anthropic](https://github.com/anthropics/anthropic-sdk-python) | `>=0.84.0,<1` | [MIT](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE) | `chat-provider-lc-anthropic`<br>`chat-provider-lc-anthropic-vertex` |
| [google-genai](https://github.com/googleapis/python-genai) | `>=1.65.0,<3` | [Apache-2.0](https://github.com/googleapis/python-genai/blob/main/LICENSE) | `chat-provider-lc-google-genai`<br>`text-embedding-provider-google` |
| [kiarina-lib-google](https://pypi.org/project/kiarina-lib-google/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) | `chat-provider-lc-anthropic-vertex`<br>`chat-provider-lc-google-genai`<br>`text-embedding-provider-google` |
| [kiarina-lib-openai](https://pypi.org/project/kiarina-lib-openai/) | `>=2.3.1` | [MIT](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) | `chat-provider-lc-openai`<br>`text-embedding-provider-openai` |
| [langchain-anthropic](https://github.com/langchain-ai/langchain-anthropic) | `>=1.0.0,<2` | [MIT](https://github.com/langchain-ai/langchain-anthropic/blob/main/LICENSE) | `chat-provider-lc-anthropic`<br>`chat-provider-lc-anthropic-vertex` |
| [langchain-google-genai](https://github.com/langchain-ai/langchain-google) | `>=4.0.0,<5` | [MIT](https://github.com/langchain-ai/langchain-google/blob/main/LICENSE) | `chat-provider-lc-google-genai` |
| [langchain-google-vertexai](https://github.com/langchain-ai/langchain-google) | `>=3.0.0,<4` | [MIT](https://github.com/langchain-ai/langchain-google/blob/main/LICENSE) | `chat-provider-lc-anthropic-vertex` |
| [langchain-openai](https://github.com/langchain-ai/langchain-openai) | `>=1.0.0,<2` | [MIT](https://github.com/langchain-ai/langchain-openai/blob/main/LICENSE) | `chat-provider-lc-openai` |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) | `text-embedding-provider-google`<br>`text-embedding-provider-mock`<br>`text-embedding-provider-openai` |
| [openai](https://github.com/openai/openai-python) | `>=2.0.1,<3` | [Apache-2.0](https://github.com/openai/openai-python/blob/main/LICENSE) | `chat-provider-lc-openai`<br>`text-embedding-provider-openai` |
| [tiktoken](https://github.com/openai/tiktoken) | `>=0.13.0` | [MIT](https://github.com/openai/tiktoken/blob/main/LICENSE) | `text-embedding-provider-openai` |
| [ulid-py](https://github.com/ahawker/ulid) | `>=1.1.0` | [Apache-2.0](https://github.com/ahawker/ulid/blob/master/LICENSE) | `chat-provider-mock` |

The `all` Extra installs every optional dependency listed above.

## Installation

```bash
pip install "kiarina-agi-text[all]"
```

## Features

- **Chat Models**
  Select a model by name or alias and receive one response or a stream. Tool calls and image, audio, video, and PDF inputs and outputs are also supported.
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
