# Chat Providers

How the `kiarina-agi-text` chat providers are built, and the vendor behavior they depend on.

## Layers

| Layer | Responsibility |
| --- | --- |
| `kiarina.agi.chat_provider` | `ChatProvider` contract, `BaseChatProvider` (request logging), `ChatCapabilities`, and the errors `TokenOverflowError`, `MaxTokenError`, and `SafetyError` |
| `kiarina.agi.chat_content` | Provider-independent content conversion: file bundles, metadata XML, merging text files, moving media a tool message cannot include into a following human turn, and `cache_control` |
| `kiarina.agi.chat_provider_impl.<name>` | One vendor SDK each: request and response conversion in `_operations`, and logging, cost, and error mapping in the provider model |

Providers call the vendor SDKs directly. There is no LangChain layer.

## Adding or Changing a Provider

- Settings extend `ChatCapabilities` and use `env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_<NAME>_"`.
- Dependencies go in a `chat-provider-<name>` extra. See [Implementation Optional Dependencies](implementation-optional-dependencies.md).
- Register the factory in `ChatProviderSettings.presets`.
- The provider is also the `MediaConverter`, returning the vendor's content part for each media type, or `None` to send only the file metadata.
- Map the vendor's stop reasons to `SafetyError` and `MaxTokenError`, and parse the vendor's context overflow error text into `TokenOverflowError`.
- Record cost from the vendor's usage. Check whether the vendor counts cached tokens inside the input token total.
- Streaming yields `AIMessageChunk` items, then the final `AIMessage`. Tool call chunks and the final tool calls must share ids.

## Testing

- Unit tests use a fake client and SDK response objects built with `model_validate`. They must pass without API keys, because CI has none.
- Costly tests call the real API with the cheapest model of the provider. Keep them few and run them only when they check something new. For high-priced models, send one short request instead of running tests. See [Update Chat Model Presets](../runbooks/update-chat-model-presets.md).
- A host without quota can be checked through a relay: give the SDK client an HTTP transport that forwards its requests to another endpoint. `test_relay_to_anthropic_api` relays Vertex AI requests to the Anthropic API.

## Vendor Notes

Checked on 2026-10-07. Recheck when a request fails in a way these notes do not explain.

### OpenAI (`openai`)

- Responses API requests use `store=False`. Reasoning items are not kept between turns.
- Chat Completions serves OpenAI-compatible local servers such as kiapi. `extra_body` passes server-specific options.
- A single message string is limited to 10,485,760 characters, which a huge prompt hits before the token limit.
- GPT-6 Astra rejects a custom `temperature`. Set `temperature` to `None` to omit it.
- GPT-6 Astra and GPT-6.1 Sol call tools only through the Responses API.

### Anthropic (`anthropic`, `anthropic_vertex`)

- Anthropic SDK 1.x does not accept `temperature` as a keyword, so it is sent in `extra_body`.
- `usage.input_tokens` excludes cache reads and cache writes. Cache writes are split into 5-minute and 1-hour TTLs.
- A refusal is `stop_reason: "refusal"`. `model_context_window_exceeded` stops the output like `max_tokens`.
- Claude Sonnet 5.5, Opus 5.5, and Fable 5.1 reject `tool_choice` of type `any` or `tool`, and nothing replaces it. The provider sends `auto` and asks for a tool call in the last user turn.
- Thinking blocks are dropped from responses and not sent back.
- The SDK uses `httpx2`. A custom `http_client` must be an `httpx2` client.
- Token counting never retries, because a failed count only skips the overflow check.

### Claude on Vertex AI (`anthropic_vertex`)

- `AsyncAnthropicVertex` needs the project when the client is created. The provider takes it from the Google settings, the credentials, or the default credentials (`GOOGLE_CLOUD_PROJECT`).
- The Claude 5 series is served from `global`, `us`, and `eu`, not `us-east5`.
- Each model is enabled in the console with an access request form and a Cloud Marketplace agreement. Fable models also need the Advanced AI Safety Addendum.
- A new project has a Claude quota of 0 and cannot request an increase until it has usage history.

### Gemini (`google_genai`)

- Gemini 3 rejects replayed function calls without a `thought_signature` (`400 INVALID_ARGUMENT`). Signatures are not kept, so the first function call of each model turn in the active loop carries `skip_thought_signature_validator`. The value is assigned after the `Part` is built, so it is sent as a string.
- Function calls and function responses carry the tool call id, because Gemini matches them by id and name.
- Function calls arrive whole in one stream chunk. Usage in a stream is cumulative, so the last chunk holds the total.
- Thought tokens are billed as output.
- `temperature` is deprecated for Gemini 3 and ignored.
