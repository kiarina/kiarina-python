# kiarina-agi-text

English | [日本語](README.ja.md)

Chat, logging, and text embedding APIs for AI agents.

## Dependencies

Required dependencies include `kiarina-agi-base`, `kiarina-agi-data`,
`kiarina-agi-file`, LangChain, and Pydantic.

Optional implementations are installed with separate extras.

| Extra | Implementation |
| --- | --- |
| `chat-provider-lc-anthropic` | Anthropic |
| `chat-provider-lc-anthropic-vertex` | Anthropic Vertex AI |
| `chat-provider-lc-google-genai` | Google Gen AI |
| `chat-provider-lc-openai` | OpenAI |
| `chat-provider-mock` | Mock chat |
| `text-embedding-provider-google` | Google embeddings |
| `text-embedding-provider-mock` | Mock embeddings |
| `text-embedding-provider-openai` | OpenAI embeddings |

## Installation

```bash
pip install kiarina-agi-text
pip install "kiarina-agi-text[chat-provider-lc-openai]"
```

## Features

### Run a Chat Model

```python
from kiarina.agi.chat_model import invoke_chat
from kiarina.agi.message import HumanMessage

message = await invoke_chat(
    [HumanMessage.create("Hello")],
    chat_options={"chat_model": "mock"},
    run_context=run_context,
)
```

### Stream a Chat Model

```python
from kiarina.agi.chat_model import stream_chat

async for chunk in stream_chat(
    messages,
    chat_options={"chat_model": "mock"},
    run_context=run_context,
):
    print(chunk.text, end="")
```

### Embed Text

```python
from kiarina.agi.text_embedding_model import embed_text

embedding = await embed_text(
    "Hello",
    text_embedding_options={"text_embedding_model": "mock"},
    run_context=run_context,
)
```

## API Reference

### `kiarina.agi.chat_logger`

`BaseChatLogger`, `chat_logger_registry`, `ChatLoggerSettings`, `settings_manager`,
`ChatLogger`, `ChatLoggerName`, `ChatLoggerSpecifier`

### `kiarina.agi.chat_model`

`invoke_chat`, `run_chat`, `stream_chat`, `ChatModel`, `ChatModelConfig`,
`chat_model_registry`, `ChatModelSettings`, `settings_manager`, `ChatModelAlias`,
`ChatModelName`, `ChatModelSpecifier`, `ChatOptions`

### `kiarina.agi.chat_provider`

`MaxTokenError`, `SafetyError`, `TokenOverflowError`, `BaseChatProvider`,
`ChatCapabilities`, `ChatProviderContext`, `ChatProviderSettings`,
`settings_manager`, `chat_provider_registry`, `ChatProviderName`, `ChatProvider`

### `kiarina.agi.langchain_chat_provider`

`from_messages`, `from_tool_infos`, `to_ai_message`, `to_ai_message_chunk`,
`LangChainChatProvider`, `LangChainMediaConverter`, `LangChainChatProviderContext`,
`LCAIMessage`, `LCAIMessageChunk`, `LCBaseMessage`, `LCContent`, `LCHumanMessage`,
`LCMessage`, `LCSystemMessage`, `LCToolCall`, `LCToolCallChunk`, `LCToolInfo`,
`LCToolMessage`, `has_content`, `normalize_content`, `remove_content`

### `kiarina.agi.text_embedding_model`

`embed_text`, `TextEmbeddingModel`, `TextEmbeddingModelConfig`,
`text_embedding_model_registry`, `TextEmbeddingModelSettings`, `settings_manager`,
`TextEmbeddingModelAlias`, `TextEmbeddingModelName`, `TextEmbeddingModelSpecifier`,
`TextEmbeddingOptions`

### `kiarina.agi.text_embedding_provider`

`BaseTextEmbeddingProvider`, `text_embedding_provider_registry`,
`TextEmbeddingProviderSettings`, `settings_manager`, `TextEmbeddingProvider`,
`TextEmbeddingProviderName`

### Implementation Packages

- `kiarina.agi.chat_logger_impl.console`: `ConsoleChatLogger`
- `kiarina.agi.chat_logger_impl.null`: `NullChatLogger`
- `kiarina.agi.chat_provider_impl.lc_anthropic`: `create_lc_anthropic_chat_provider`, `LCAnthropicChatProvider`, `LCAnthropicChatProviderSettings`, `settings_manager`
- `kiarina.agi.chat_provider_impl.lc_anthropic_vertex`: `create_lc_anthropic_vertex_chat_provider`, `LCAnthropicVertexChatProvider`, `LCAnthropicVertexChatProviderSettings`, `settings_manager`
- `kiarina.agi.chat_provider_impl.lc_google_genai`: `create_lc_google_genai_chat_provider`, `LCGoogleGenAIChatProvider`, `LCGoogleGenAIChatProviderSettings`, `settings_manager`
- `kiarina.agi.chat_provider_impl.lc_openai`: `create_lc_openai_chat_provider`, `LCOpenAIChatProvider`, `LCOpenAIChatProviderSettings`, `settings_manager`
- `kiarina.agi.chat_provider_impl.mock`: `create_mock_chat_provider`, `MockChatProvider`, `MockChatProviderSettings`, `settings_manager`
- `kiarina.agi.text_embedding_provider_impl.google`: `create_google_text_embedding_provider`, `GoogleTextEmbeddingProvider`, `GoogleTextEmbeddingProviderSettings`, `settings_manager`
- `kiarina.agi.text_embedding_provider_impl.mock`: `create_mock_text_embedding_provider`, `MockTextEmbeddingProvider`, `MockTextEmbeddingProviderSettings`, `settings_manager`
- `kiarina.agi.text_embedding_provider_impl.openai`: `create_openai_text_embedding_provider`, `OpenAITextEmbeddingProvider`, `OpenAITextEmbeddingProviderSettings`, `settings_manager`
