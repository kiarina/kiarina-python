# Decide when to deprecate the LangChain chat providers

## Background

kiarina-agi-text now has chat providers that call the vendor SDKs directly:
`openai` (replaces `lc_openai`), `anthropic` (replaces `lc_anthropic`), and
`anthropic_vertex` (replaces `lc_anthropic_vertex`). The OpenAI, local, and `claude-*`
presets use them. The LangChain providers remain for users who reference them by name.

## Before switching the vclaude presets

- `anthropic_vertex` is covered by unit tests only. Run
  `make chat_provider_anthropic_vertex_test` with a project that can call Claude on
  Vertex AI (put `kiarina.lib.google` settings in
  `tests/chat_provider_impl/anthropic_vertex/test_settings.yaml`), then switch the
  `vclaude-*` presets and drop their `token_count_model_name`, since token counting
  now goes through Vertex AI with the Vertex model names.
- On 2026-10-07 no project on the development machine worked: one had no Claude
  models enabled, another returned 429 for every request and for count-tokens.
- `lc_anthropic_vertex` fails on Anthropic SDK 1.x when `temperature` is set
  (`ChatAnthropicVertex` passes it as a keyword), so `vclaude-haiku-4-5` is broken today.

## To decide

- When to mark the `lc_*` providers as deprecated, and when to remove them with their
  `chat-provider-lc-*` extras.
- Check first whether any project still sets `provider_name: lc_openai`,
  `lc_anthropic`, or `lc_anthropic_vertex`, or their
  `KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_*` env vars (none found in the kiarina
  repositories on 2026-10-07).

## Follow-up candidates

- Keep reasoning across turns with `include=["reasoning.encrypted_content"]` on the
  OpenAI Responses API. `AIMessage` needs a place to hold the encrypted items.
- The local thinking model (`qwen3.8-flash-next` on kiapi) returns its reasoning inside
  `content` followed by `</think>`, with both OpenAI providers.
