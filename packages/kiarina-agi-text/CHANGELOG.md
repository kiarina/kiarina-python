# Changelog

All notable changes to the kiarina-agi-text package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Add the `codex` chat provider (`kiarina.agi.chat_provider_impl.codex`), which runs `codex app-server` with the local Codex login (a ChatGPT subscription). Install it with the `chat-provider-codex` extra.
  - Each request starts a new process and ephemeral thread, injects the conversation as raw Responses API items (`thread/inject_items`), and turns off Codex's own tools, instructions, and MCP servers.
  - The request ends when the first model response completes, with tool call requests left unanswered, so the caller runs the tools and the model gets no second request.
  - With `thread_reuse` (default on), the process and thread are kept after a response, and the next request that extends the same history continues them, answering the held tool call requests or starting a new turn. Codex reads the prompt cache only within a thread. `thread_idle_timeout` and `max_live_threads` limit the kept threads.
  - The model entry is copied from Codex's cached model list with direct tool calls, because new models otherwise call tools only from a JavaScript cell.
- Add the `claude_code` chat provider (`kiarina.agi.chat_provider_impl.claude_code`), which runs Claude Code through the Claude Agent SDK with the local Claude login (a Claude subscription). Install it with the `chat-provider-claude-code` extra.
  - Each request starts a new session, sends the conversation as `<messages>` XML with one content block per message, turns off Claude Code's own tools and settings, and stops after the first model turn (`max_turns=1`).
  - A cache breakpoint on the last message lets the next request, which only appends, read the conversation from the prompt cache.
  - Inherited `ANTHROPIC_*` and `CLAUDE_CODE_*` environment variables are cleared, so an API key or a host Claude Code session does not take over the login.
- Add hidden chat model presets for the two providers, which record zero cost: `codex-gpt-6-astra`, `codex-gpt-6.1-sol`, and `codex-gpt-6-luna`, and `claude-code-sonnet-5-5`, `claude-code-opus-5-5`, `claude-code-fable-5-1`, and `claude-code-haiku-4-5`. The `codex` and `claude_code` aliases point to `codex-gpt-6.1-sol` and `claude-code-opus-5-5`.
- Add `ChatProviderState`, `find_chat_provider_state`, `collect_message_states`, `compute_history_hash`, `compute_message_hashes`, and `CHAT_PROVIDER_STATE_KEY` to `kiarina.agi.chat_provider`: the convention for a chat provider to keep state on the `AIMessage` it returns (in `metadata["chat_provider"]`), with the hash of the history up to that message, and to use it only while the history still matches.
- `anthropic` and `anthropic_vertex` keep thinking blocks and send them back unchanged with their turn, as the models with thinking always on ask for.
- `openai` (Responses API) asks for encrypted reasoning items and sends them back with their turn. `carry_reasoning` turns it off.
- `google` keeps the thought signatures of function calls and text and sends them back, instead of the signature bypass where one was kept.
- Add `to_transcript` and `Transcript` to `kiarina.agi.chat_content`, which flatten messages into a system prompt and `<messages>` XML, as one text or as one part per message.

### Changed (BREAKING)
- Rename the `google_genai` chat provider to `google` (`kiarina.agi.chat_provider_impl.google`, `GoogleChatProvider`, `GoogleChatProviderSettings`, `create_google_chat_provider`), its settings prefix to `KIARINA_AGI_CHAT_PROVIDER_IMPL_GOOGLE_`, and its extra to `chat-provider-google`, so chat providers are named after what they call, like the `google` text embedding provider.

## [2.35.0] - 2026-10-07

### Added
- Add the `qwen3.8-27b` chat model preset for the kiapi Qwen3.8-27B model (without thinking).
- Add the `google_genai` chat provider (`kiarina.agi.chat_provider_impl.google_genai`), which calls Gemini with the google-genai SDK directly instead of LangChain, through the Gemini API or Vertex AI, with the same settings as `lc_google_genai`. Install it with the `chat-provider-google-genai` extra.
  - `SAFETY`, `PROHIBITED_CONTENT`, `BLOCKLIST`, `SPII`, `RECITATION`, and image safety finish reasons, and blocked prompts, raise `SafetyError`. `lc_google_genai` only checked for `safety` in the finish reason.
  - Function calls replayed to Gemini 3 carry the thought signature bypass, as `lc_google_genai` did, because `AIMessage` does not keep signatures.
  - Function calls and function responses carry the tool call id, as Gemini requires them to match by id and name.
- Add the `anthropic` chat provider (`kiarina.agi.chat_provider_impl.anthropic`), which calls the Anthropic SDK directly instead of LangChain, with the same settings as `lc_anthropic`. Install it with the `chat-provider-anthropic` extra.
  - A `refusal` stop reason raises `SafetyError`. `lc_anthropic` checked for a `safety` stop reason, which the API does not return.
  - A `model_context_window_exceeded` stop reason raises `MaxTokenError`.
  - Retries are left to the SDK (`max_retry_count`), so a failed stream is no longer restarted after chunks were yielded. The token count check is never retried.
  - For models that reject forced tool choice (Claude Sonnet 5.5, Opus 5.5, and Fable 5.1), a `tool_choice` of `any` or a tool name falls back to `auto`, and the last user turn asks the model to call a tool.
- Add the `anthropic_vertex` chat provider (`kiarina.agi.chat_provider_impl.anthropic_vertex`), which calls Claude on Vertex AI with the Anthropic SDK. Install it with the `chat-provider-anthropic-vertex` extra.
  - Token counting goes through Vertex AI, so no Anthropic API key is needed. `token_count_model_name` defaults to `model_name`.
  - The project comes from `kiarina.lib.google` settings, the credentials, or the default credentials and `GOOGLE_CLOUD_PROJECT`.
- Add the `openai` chat provider (`kiarina.agi.chat_provider_impl.openai`), which calls the OpenAI SDK directly instead of LangChain. It supports the Chat Completions API and the Responses API through `endpoint_type`, with the same settings as `lc_openai` except `tiktoken_model_name`. Install it with the `chat-provider-openai` extra.
  - The endpoint follows `endpoint_type` only. Unlike `lc_openai`, a PDF input does not switch Chat Completions requests to the Responses API; Chat Completions sends PDFs as `file` parts.
  - Responses API requests detect `max_output_tokens` and `content_filter` incompletions and raise `MaxTokenError` and `SafetyError`.
  - `temperature` accepts `None` to omit it, for models that reject a custom temperature such as GPT-6 Astra.
- Add `kiarina.agi.chat_content`, which converts message contents and files into provider content parts without depending on LangChain. It provides `MediaConverter`, `ContentPart`, `ContentParts`, and `from_contents`.

### Changed (BREAKING)
- Update the chat model presets to the current models (checked 2026-10-07). Removed presets: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.4-mini`, `gpt-5.4-nano`, `claude-sonnet-5`, `claude-opus-5`, `claude-fable-5`, `vclaude-sonnet-5`, `vclaude-opus-5`, `vclaude-fable-5`, and `gemini-3.6-flash`.
  - OpenAI: `gpt-6-astra`, `gpt-6.1-sol`, and `gpt-6-luna`. `gpt-6-luna` is the named successor of `gpt-5.4-nano`, which is deprecated. GPT-6 has no Terra tier, and `gpt-6-luna` is cheaper than `gpt-5.4-mini` with a larger context.
  - Anthropic: `claude-sonnet-5-5`, `claude-opus-5-5`, and `claude-fable-5-1`, and the same models as `vclaude-*`. Claude Sonnet 5 pricing is corrected to $2/$10 per MTok.
  - Google: `gemini-3.8-flash`, which replaces `gemini-3.6-flash` (retired on Vertex AI on 2026-11-19) at the same list price.
  - `claude-haiku-4-5` and `vclaude-haiku-4-5` allow 64K output tokens.
  - The `vclaude-*` presets use the `global` Vertex AI location, because the Claude 5 series is not served from `us-east5`.
  - The `llm`, `vlm`, and `openai` aliases resolve to `gpt-6.1-sol`, `anthropic` to `claude-sonnet-5-5`, and `omni` and `google` to `gemini-3.8-flash`.

### Changed
- Every chat model preset uses the SDK providers (`openai`, `anthropic`, `anthropic_vertex`, and `google_genai`) instead of the `lc_*` providers.

### Removed (BREAKING)
- Remove the LangChain chat providers `lc_openai`, `lc_anthropic`, `lc_anthropic_vertex`, and `lc_google_genai`, the `kiarina.agi.langchain_chat_provider` package (including `LangChainMediaConverter`), and the `chat-provider-lc-*` extras. Use the `openai`, `anthropic`, `anthropic_vertex`, and `google_genai` providers instead. `langchain` and `langchain-core` are no longer dependencies.
- Remove the `lc_google` chat provider preset, which pointed to a module that does not exist.

## [2.33.0] - 2026-09-24

### Changed (BREAKING)
- Replace the `qwen3.6` and `qwen3.6-fast` chat model presets with `qwen3.8-flash-next` and `qwen3.8-flash-next-fast`. Both call the kiapi `qwen3.8-flash-next` model (Qwen3.8-Flash-Next), with and without thinking. The `local` alias now resolves to `qwen3.8-flash-next-fast`. kiapi is dropping `qwen3.6-27b`.

## [2.28.0] - 2026-09-05

### Changed
- Support OpenAI Python 3.x.
- Support Anthropic Python 1.x.

## [2.22.1] - 2026-08-16

### Changed
- Set the `qwen3.6`, `qwen3.6-fast`, and `qwen3-omni` costs to zero. Local models incur no API charge, and the `lc_openai` provider defaults are not zero.

## [2.19.0] - 2026-07-27

### Added
- Add prefix text for converted file bundle media in chat messages.

### Fixed
- Support OpenAI tiered pricing and prompt cache write costs in cost records.

## [2.17.0] - 2026-07-26

### Changed
- Update chat model presets and aliases for current OpenAI, Anthropic, and Google models.

### Fixed
- Omit the deprecated `temperature` parameter from Claude 5 requests.

## [2.8.0] - 2026-07-08

### Changed
- Update `LCAnthropicVertexChatProvider` to use `get_cloud_options` from `kiarina-lib-google`.
- Use `kiarina-lib-google` to resolve Google Gen AI client options for Google chat and text embedding providers.

## [2.7.0] - 2026-07-06

### Added
- Add the `kiarina-agi-text` package.

### Changed
- Expand the package README with dependencies, installation, usage, configuration, and public API references.
- Add an `all` extra and consolidate optional dependency documentation.
- Add concrete type annotations to package tests and remove file-wide mypy suppressions.
- Add the GPT-5.5 chat model preset and remove obsolete OpenAI presets.
- Select chat model helper tests through `KIARINA_AGI_TEXT_TEST_CHAT_MODEL`, default to the mock model, configure verbose parallel retries and timeouts, use a smaller text fixture, and hide unsupported chat model presets.
- Show the selected chat model in pytest output and load package test variables from `.env.vscode` in VS Code.
- Move manually run chat and token overflow checks from skipped tests to package scripts.
- Enable targeted costly tests through `KIARINA_TEST_COSTLY`, the test task, and package Make shortcuts.

### Fixed
- Allow chat helpers to create a run context when one is not provided.

## [2.6.0] - 2026-07-03

### Added
- Add chat logging, chat models, chat providers, and text embedding APIs.
- Add optional Anthropic, Google, OpenAI, and mock implementations.
