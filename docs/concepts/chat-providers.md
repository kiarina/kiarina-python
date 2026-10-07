# Chat Providers

How the `kiarina-agi-text` chat providers are built, and the vendor behavior they depend on.

## Layers

| Layer | Responsibility |
| --- | --- |
| `kiarina.agi.chat_provider` | `ChatProvider` contract, `BaseChatProvider` (request logging), `ChatCapabilities`, and the errors `TokenOverflowError`, `MaxTokenError`, and `SafetyError` |
| `kiarina.agi.chat_content` | Provider-independent content conversion: file bundles, metadata XML, merging text files, moving media a tool message cannot include into a following human turn, `cache_control`, and the `<messages>` XML transcript for runtimes that take one prompt |
| `kiarina.agi.chat_provider_impl.<name>` | One vendor SDK each: request and response conversion in `_operations`, and logging, cost, and error mapping in the provider model |

Providers call the vendor SDKs directly. There is no LangChain layer.

`codex_app_server` and `claude_agent_sdk` are different: they run the Codex and Claude Code agents with the local subscription logins, as one-turn chat models. See [Subscription Runtimes](#subscription-runtimes-codex_app_server-claude_agent_sdk).

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
- `codex_app_server` and `claude_agent_sdk` tests use a fake `codex app-server` script and a fake `claude_agent_sdk.query`. To see what a runtime really sends without using the subscription, point it at a local capture server: `config_overrides` with a `model_providers` entry for Codex, and `env` with `ANTHROPIC_BASE_URL` and a dummy `ANTHROPIC_API_KEY` for Claude Code.
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

### Subscription Runtimes (`codex_app_server`, `claude_agent_sdk`)

Checked with Codex 0.160.1 and Claude Agent SDK 0.2.164 (Claude Code 2.1.292). The experiments, captures, and measurements are in the [agent-runtimes-as-llm-api lab](https://github.com/kiarina/labs/tree/main/2026/10/07/agent-runtimes-as-llm-api).

- Each request starts a new process and session. Startup adds a few seconds per request.
- Claude Code gets the conversation as `<messages>` XML (`to_transcript`), one content block per message, with how to read it in the system prompt. Codex gets it as raw Responses API items through `thread/inject_items`, as the API would, and the turn starts with no input.
- The runtime's own tools, instructions, settings, and MCP servers are turned off, so the model sees only the caller's instructions, tools, and transcript. Claude Code still adds one line naming the SDK and a short environment section.
- The run must stop after the first model turn without running the tools and without a second model request:
  - Claude Code runs with `max_turns=1`. It calls the tool handlers before it stops, so they return a placeholder. Stopping the stream at `message_stop` does not work: Claude Code sends the interrupted tool results to the model. A PreToolUse hook returning `defer` stops it too, but reports only one tool call. The SDK raises `ResultError` after the `error_max_turns` result, which is expected.
  - Claude Code sends each tool use of a turn as its own assistant message, and starts the first handler before the second arrives.
  - Codex requests one tool call at a time and waits for each reply. The provider never replies. With `experimentalRawEvents`, every response item arrives as `rawResponseItem/completed` before any tool runs, and `rawResponse/completed` ends the response with its usage. The provider closes the process there.
  - Codex sends app tools with `parallel_tool_calls: false`. `supports_parallel_tool_calls` is an MCP server setting and does not change it.
- New Codex models call tools only from inside a JavaScript cell (`tool_mode: code_mode_only` in `~/.codex/models_cache.json`). Neither features nor `thread/start` config change it. The provider copies the model entry with the tool mode cleared into its own `model_catalog_json`. Codex updates can change these fields.
- Codex config (`features.*`, `model_catalog_json`) takes effect only as `--config` when the process starts. `baseInstructions` is sent as a developer message.
- The Claude Agent SDK passes the parent environment to Claude Code. An inherited `ANTHROPIC_API_KEY` would bill the API, and a host Claude Code session's `CLAUDE_CODE_*` variables would lend its login, so the provider sets them to empty strings, which Claude Code treats as unset. `--name` stops Claude Code from sending the whole prompt again to name the session.
- Prompt caching, measured with two requests that share a 5K-token history:
  - Claude caches block by block, so a transcript in one text block never matches the next request (773 of about 5,100 input tokens read from the cache). With one block per message and a breakpoint on the last one, the second request read 4,508 tokens and wrote 588.
  - Claude Code adds three breakpoints (two in the system prompt, one on the environment section it appends after the user turn), so the provider's is the fourth and last the API allows. Claude Code's use the 1-hour TTL, and a 5-minute breakpoint may not come before a 1-hour one (`400`), so the provider's uses 1 hour too.
  - Codex read and wrote nothing across new threads, with the history in one message or as items, at 3K and 12K tokens. Within one thread the lab's later requests did read the cache. GPT-6 itself caches at the end of the latest message only, and `prompt_cache_key`, which Codex sets to the thread id, only separates accounting on the API.
- Usage is recorded at zero cost. Claude Code reports what the request would cost on the API (`total_cost_usd`), kept as `api_cost_microdollars`. Codex's `inputTokens` includes cached tokens.
- The subscription context window can be smaller than the API's. Codex's model list gives GPT-6.1 Sol 272K.
- Claude tends to point out contradictions in the transcript, including its own earlier messages, even when not asked.
- These runtimes are for the user's own login. Whether they may serve other people under a subscription depends on each vendor's terms, which keep changing.
