# Decide when to deprecate the lc_openai chat provider

## Background

kiarina-agi-text now has the `openai` chat provider, which calls the OpenAI SDK directly.
All OpenAI and local chat model presets use it. `lc_openai` remains only for users who
reference it by name in their own model configs.

## To decide

- When to mark `lc_openai` as deprecated, and when to remove it with the `chat-provider-lc-openai` extra.
- Check first whether any project still sets `provider_name: lc_openai` or the
  `KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_OPENAI_` env vars (none found in the kiarina repositories on 2026-10-07).

## Follow-up candidates for the openai provider

- Keep reasoning across turns with `include=["reasoning.encrypted_content"]` on the Responses API.
  `AIMessage` needs a place to hold the encrypted items. Today reasoning is dropped, as in `lc_openai`.
- The local thinking model (`qwen3.8-flash-next` on kiapi) returns its reasoning inside `content`
  followed by `</think>`, with both providers. Splitting it belongs to the server or a later provider option.
