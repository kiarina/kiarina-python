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

`all` Extra は、上記の optional dependency をすべて導入します。

## Installation

```bash
pip install "kiarina-agi-text[all]"
```

## Features

- **Chat Models**
  名前または alias でモデルを選択し、単発応答またはストリームを取得します。ツール呼び出しと画像、音声、動画、PDF の入出力にも対応します。
- **Text Embeddings**
  登録済みモデルを選択し、同じ API でテキストをベクトル化します。

### Chat Models

`RunContext` はすべての呼び出しで必須です。以下の例では、外部 API の認証情報が不要な mock model を明示的に選択しています。

単発の応答を取得するには `invoke_chat` を使用します。

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

ストリームを処理するには `stream_chat` を使用します。`AIMessageChunk` と、最後の `AIMessage` が順に返ります。

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

`run_chat` は `chat_options["streaming"]` に応じて、単発応答またはストリームを同じ反復インターフェースで返します。

```python
from kiarina.agi.chat_model import run_chat

async for item in run_chat(
    [HumanMessage.create("Hello")],
    chat_options={"chat_model": "mock", "streaming": False},
    run_context=RunContext(),
):
    print(item.text, end="")
```

ツールをモデルに渡し、ツールの選択方法と並列呼び出しを指定できます。

```python
from pydantic import BaseModel, Field

from kiarina.agi.tool_info import create_tool_info


class GetWeather(BaseModel):
    location: str = Field(description="Location to get the weather for")


message = await invoke_chat(
    [HumanMessage.create("What is the weather in Tokyo?")],
    tool_infos=[
        create_tool_info(GetWeather, description="Get the weather for a location")
    ],
    chat_options={
        "chat_model": "mock",
        "tool_choice": "auto",
        "parallel_tool_calls": True,
    },
    run_context=RunContext(),
)
```

`HumanMessage.create` の第 2 引数に file info を渡すと、画像、音声、動画、PDF を入力できます。

```python
message = await invoke_chat(
    [HumanMessage.create("What do you see in this image?", [image_file_info])],
    chat_options={"chat_model": "mock"},
    run_context=RunContext(),
)
```

`HumanMessage`、`AIMessage`、`AIMessageChunk`、`ToolMessage`、`ToolInfo`、`Embedding` など、チャットの入出力とテキスト埋め込みで使用するデータ型は [kiarina-agi-data](../kiarina-agi-data/) で定義されています。

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

`embed_text` は、ベクトルとその embedding space を保持する `Embedding` を返します。

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
