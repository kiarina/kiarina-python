# Decide when to deprecate the LangChain chat providers

## Background

kiarina-agi-text now has chat providers that call the vendor SDKs directly:
`openai` (replaces `lc_openai`), `anthropic` (replaces `lc_anthropic`),
`anthropic_vertex` (replaces `lc_anthropic_vertex`), and `google_genai` (replaces
`lc_google_genai`). Every chat model preset uses them. The LangChain providers remain for users who reference them by name.

## Vertex AI live check

- All `vclaude-*` presets use `anthropic_vertex`. Its Vertex request path is checked by
  `test_relay_to_anthropic_api`, which relays the SDK's Vertex requests to the Anthropic API.
- Not yet checked against Vertex AI itself. On 2026-10-07 Claude Haiku 4.5, Sonnet 5, Opus 5,
  and Fable 5 were enabled in the `blazeworks` project, but its Claude quota is 0 (`429` on
  every call and on count-tokens, in `us-east5` and `global`). New projects cannot request an
  increase until they have usage history. When calls go through, run
  `make chat_provider_anthropic_vertex_test` with `kiarina.lib.google` settings in
  `tests/chat_provider_impl/anthropic_vertex/test_settings.yaml`.
- `lc_anthropic_vertex` fails on Anthropic SDK 1.x when `temperature` is set
  (`ChatAnthropicVertex` passes it as a keyword).

## To decide

- When to mark the `lc_*` providers as deprecated, and when to remove them with their
  `chat-provider-lc-*` extras.
- Check first whether any project still sets `provider_name: lc_openai`,
  `lc_anthropic`, `lc_anthropic_vertex`, or `lc_google_genai`, or their
  `KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_*` env vars (none found in the kiarina
  repositories on 2026-10-07).

## Follow-up candidates

- Give `AIMessage` a place for provider-opaque state, then carry reasoning across turns:
  OpenAI Responses `reasoning.encrypted_content` (with `include=[...]`) and Gemini 3
  `thought_signature` on function calls. Today both are dropped, and `google_genai`
  sends the documented `skip_thought_signature_validator` bypass instead, which
  Gemini accepts but which loses the reasoning context between tool calls.
- The local thinking model (`qwen3.8-flash-next` on kiapi) returns its reasoning inside
  `content` followed by `</think>`, with both OpenAI providers.
