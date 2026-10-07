# Chat Providers

How the `kiarina-agi-text` chat providers are built, and the vendor behavior they depend on.

## Layers

| Layer | Responsibility |
| --- | --- |
| `kiarina.agi.chat_provider` | `ChatProvider` contract, `BaseChatProvider` (request logging), `ChatCapabilities`, and the errors `TokenOverflowError`, `MaxTokenError`, and `SafetyError` |
| `kiarina.agi.chat_content` | Provider-independent content conversion: file bundles, metadata XML, merging text files, moving media a tool message cannot include into a following human turn, `cache_control`, and the `<messages>` XML transcript for runtimes that take one prompt |
| `kiarina.agi.chat_provider_impl.<name>` | One target each: request and response conversion in `_operations`, and logging, cost, and error mapping in the provider model |

Providers call the vendor SDKs directly. There is no LangChain layer.

`codex` and `claude_code` are different: they run the Codex and Claude Code agents with the local subscription logins, as one-turn chat models. See [Subscription Runtimes](#subscription-runtimes-codex-claude_code).

## Adding or Changing a Provider

- Name a provider after what it calls (`openai`, `anthropic`, `google`, `codex`, `claude_code`), not after its SDK or protocol. A second interface to the same target becomes a setting of that provider, as `openai` switches the Chat Completions and Responses APIs with `endpoint_type`, and `google` the Gemini API and Vertex AI. A different host of another vendor's model gets its own provider (`anthropic_vertex`).
- Settings extend `ChatCapabilities` and use `env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_<NAME>_"`.
- Dependencies go in a `chat-provider-<name>` extra. See [Implementation Optional Dependencies](implementation-optional-dependencies.md).
- Register the factory in `ChatProviderSettings.presets`.
- The provider is also the `MediaConverter`, returning the vendor's content part for each media type, or `None` to send only the file metadata.
- Map the vendor's stop reasons to `SafetyError` and `MaxTokenError`, and parse the vendor's context overflow error text into `TokenOverflowError`.
- Record cost from the vendor's usage. Check whether the vendor counts cached tokens inside the input token total.
- Streaming yields `AIMessageChunk` items, then the final `AIMessage`. Tool call chunks and the final tool calls must share ids.

## Provider State

A provider can keep state on the `AIMessage` it returns, to continue from it in a later request: a thread to resume, or reasoning to send back.

- It is a `ChatProviderState` in `message.metadata["chat_provider"]`: the provider name, `history_hash`, and provider-specific `data`. `Message.metadata` is a free dict in kiarina-agi-data, which knows nothing about chat providers; the key is only known here.
- `history_hash` is the hash of the history up to and including that message, and the provider uses the state only while it still matches, so edits to the history (file shrinking, summaries, retries) make the provider start fresh and correctness never depends on the state:
  - A thread (`codex`): `compute_history_hash` of the history in the form the provider sends it. `find_chat_provider_state` returns the last AI message's state, and the provider continues only if the hash matches its conversion of the new history up to that message.
  - Reasoning (`anthropic`, `openai`, `google`): `compute_message_hashes`, a chained hash over the messages (type, text, tool calls, tool result fields) with the model name, computed in one pass. `collect_message_states` returns every AI message whose state still matches. An edit drops the reasoning of the AI messages after it and keeps the ones before it. Reasoning sent with a history it was not written for could rely on facts the model can no longer see, and the 5.5 Claude models keep earlier turns' thinking in context, so a mismatch sends none; the APIs accept a turn without it.
- Metadata is never sent to a model. Code that displays message metadata should skip the `chat_provider` key, whose values can be large.
- Only the final `AIMessage` of a stream carries the state.

## Testing

- Unit tests use a fake client and SDK response objects built with `model_validate`. They must pass without API keys, because CI has none.
- Costly tests call the real API with the cheapest model of the provider. Keep them few and run them only when they check something new. For high-priced models, send one short request instead of running tests. See [Update Chat Model Presets](../runbooks/update-chat-model-presets.md).
- `codex` and `claude_code` tests use a fake `codex app-server` script and a fake `claude_agent_sdk.query`. To see what a runtime really sends without using the subscription, point it at a local capture server: `config_overrides` with a `model_providers` entry for Codex, and `env` with `ANTHROPIC_BASE_URL` and a dummy `ANTHROPIC_API_KEY` for Claude Code.
- A capture server accepts whatever it gets, so it cannot catch what the real API rejects. A 1-hour cache breakpoint after a 5-minute one passed the capture server and failed live with `400`.
- A host without quota can be checked through a relay: give the SDK client an HTTP transport that forwards its requests to another endpoint. `test_relay_to_anthropic_api` relays Vertex AI requests to the Anthropic API.

## Vendor Notes

Checked on 2026-10-08. Recheck when a request fails in a way these notes do not explain.

### OpenAI (`openai`)

- Responses API requests use `store=False`, so reasoning is kept only by asking for `include=["reasoning.encrypted_content"]`. The encrypted reasoning items are kept as provider state and sent back before their message's items (`carry_reasoning`). A model that does not reason on a request, such as GPT-6 Luna on an easy tool call, returns none.
- Chat Completions serves OpenAI-compatible local servers such as kiapi. `extra_body` passes server-specific options.
- A single message string is limited to 10,485,760 characters, which a huge prompt hits before the token limit.
- GPT-6 Astra rejects a custom `temperature`. Set `temperature` to `None` to omit it.
- GPT-6 Astra and GPT-6.1 Sol call tools only through the Responses API.

### Anthropic (`anthropic`, `anthropic_vertex`)

- Anthropic SDK 1.x does not accept `temperature` as a keyword, so it is sent in `extra_body`.
- `usage.input_tokens` excludes cache reads and cache writes. Cache writes are split into 5-minute and 1-hour TTLs.
- A refusal is `stop_reason: "refusal"`. `model_context_window_exceeded` stops the output like `max_tokens`.
- Claude Sonnet 5.5, Opus 5.5, and Fable 5.1 reject `tool_choice` of type `any` or `tool`, and nothing replaces it. The provider sends `auto` and asks for a tool call in the last user turn.
- Thinking blocks (`thinking`, `redacted_thinking`) are kept as provider state and sent back unchanged at the start of their turn. The 5.5 models think adaptively, with `display: "omitted"` by default: a block has an empty `thinking` field and a signature that carries the encrypted thinking. On an easy request the model may not think, and no block comes back. Modified blocks are rejected with `400`.
- The SDK uses `httpx2`. A custom `http_client` must be an `httpx2` client.
- Token counting never retries, because a failed count only skips the overflow check.

### Claude on Vertex AI (`anthropic_vertex`)

- `AsyncAnthropicVertex` needs the project when the client is created. The provider takes it from the Google settings, the credentials, or the default credentials (`GOOGLE_CLOUD_PROJECT`).
- The Claude 5 series is served from `global`, `us`, and `eu`, not `us-east5`.
- Each model is enabled in the console with an access request form and a Cloud Marketplace agreement. Fable models also need the Advanced AI Safety Addendum.
- A new project has a Claude quota of 0 and cannot request an increase until it has usage history.

### Gemini (`google`)

- Gemini 3 rejects replayed function calls without a `thought_signature` (`400 INVALID_ARGUMENT`). The signatures on function call parts (by tool call id) and on the text are kept as provider state and put back on their parts. A first function call of a model turn in the active loop with no kept signature carries `skip_thought_signature_validator` instead. The value is assigned after the `Part` is built, so it is sent as a string.
- Function calls and function responses carry the tool call id, because Gemini matches them by id and name.
- Function calls arrive whole in one stream chunk. Usage in a stream is cumulative, so the last chunk holds the total.
- Thought tokens are billed as output.
- `temperature` is deprecated for Gemini 3 and ignored.

### Subscription Runtimes (`codex`, `claude_code`)

Checked with Codex 0.160.1 and Claude Agent SDK 0.2.164 (Claude Code 2.1.292). The experiments, captures, and measurements are in the [agent-runtimes-as-llm-api lab](https://github.com/kiarina/labs/tree/main/2026/10/07/agent-runtimes-as-llm-api).

- Each request starts a new process and session, which adds a few seconds, except when `codex` continues a kept thread (below).
- Claude Code gets the conversation as `<messages>` XML (`to_transcript`), one content block per message, with how to read it in the system prompt. Codex gets it as raw Responses API items through `thread/inject_items`, as the API would, and the turn starts with no input.
- The runtime's own tools, instructions, settings, and MCP servers are turned off, so the model sees only the caller's instructions, tools, and transcript. Claude Code still adds one line naming the SDK and a short environment section.
- The run must stop after the first model turn without running the tools and without a second model request:
  - Claude Code runs with `max_turns=1`. It calls the tool handlers before it stops, so they return a placeholder. Stopping the stream at `message_stop` does not work: Claude Code sends the interrupted tool results to the model. A PreToolUse hook returning `defer` stops it too, but reports only one tool call. The SDK raises `ResultError` after the `error_max_turns` result, which is expected.
  - Claude Code sends each tool use of a turn as its own assistant message, and starts the first handler before the second arrives.
  - Codex requests one tool call at a time and waits for each reply. The provider holds the request instead of running the tool. With `experimentalRawEvents`, every response item arrives as `rawResponseItem/completed` before any tool runs, and `rawResponse/completed` ends the response with its usage. The provider stops there, and closes or keeps the process.
  - Codex sends app tools with `parallel_tool_calls: false`. `supports_parallel_tool_calls` is an MCP server setting and does not change it.
- New Codex models call tools only from inside a JavaScript cell (`tool_mode: code_mode_only` in `~/.codex/models_cache.json`). Neither features nor `thread/start` config change it. The provider copies the model entry with the tool mode cleared into its own `model_catalog_json`. Codex updates can change these fields.
- Codex config (`features.*`, `model_catalog_json`) takes effect only as `--config` when the process starts. `baseInstructions` is sent as a developer message.
- The Claude Agent SDK passes the parent environment to Claude Code. An inherited `ANTHROPIC_API_KEY` would bill the API, and a host Claude Code session's `CLAUDE_CODE_*` variables would lend its login, so the provider sets them to empty strings, which Claude Code treats as unset. `--name` stops Claude Code from sending the whole prompt again to name the session.
- Prompt caching, measured with two requests that share a 5K-token history:
  - Claude caches block by block, so a transcript in one text block never matches the next request (773 of about 5,100 input tokens read from the cache). With one block per message and a breakpoint on the last one, the second request read 4,508 tokens and wrote 588.
  - Claude Code adds three breakpoints (two in the system prompt, one on the environment section it appends after the user turn), so the provider's is the fourth and last the API allows. Claude Code's use the 1-hour TTL, and a 5-minute breakpoint may not come before a 1-hour one (`400`), so the provider's uses 1 hour too.
  - GPT-6 caches at the end of the latest message only, and `prompt_cache_key`, which Codex sets to the thread id, only separates accounting on the API. Even so, Codex read nothing across new threads, with the history in one message or as items, at 3K and 12K tokens. Within one thread a resumed turn read 11,520 of 11,697 tokens at 12K, and nothing at 3.3K. Codex reports no cache writes either way.
- `codex` therefore keeps the process and thread after a response (`thread_reuse`), and records the thread id and the history hash as `ChatProviderState` on the returned message. When the next request extends that history, a paused turn gets the tool results as replies to its held requests, and a completed turn gets the new messages injected and a new turn. Anything else, including an edited history, a forced tool choice, or a dead process, starts a new thread. Kept threads live in a per-process pool (`thread_idle_timeout`, `max_live_threads`) and end with the program, because their stdin closes. Through the provider with a 12K history, the resumed request read 11,392 tokens from the cache and took 2.5 seconds instead of 4.2.
- On the live server, Codex's tool call request (`item/tool/call`) arrives before `rawResponse/completed`. Injected items are echoed with `turnId: "auto-compact-0"`, and `turn/completed` carries its turn id in `turn.id`.
- Usage is recorded at zero cost. Claude Code reports what the request would cost on the API (`total_cost_usd`), kept as `api_cost_microdollars`. Codex's `inputTokens` includes cached tokens.
- The subscription context window can be smaller than the API's. Codex's model list gives GPT-6.1 Sol 272K.
- `claude_code` sends the conversation as XML text in one user turn, so there is nowhere to send thinking blocks back; it keeps no reasoning state.
- `claude_code` starts a new session for every request, on purpose. The Claude Agent SDK could keep one (`ClaudeSDKClient`), with tool handlers held like Codex's requests, but Anthropic caches by content across sessions, so the cache already works; keeping it would save only the startup seconds, against the cost of a session pool and unverified handler timeouts.
- Claude tends to point out contradictions in the transcript, including its own earlier messages, even when not asked.
- These runtimes are for the user's own login. Whether they may serve other people under a subscription depends on each vendor's terms, which keep changing.
