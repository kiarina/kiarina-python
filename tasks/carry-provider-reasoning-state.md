# Carry provider reasoning state across turns

## Background

`AIMessage` keeps only text contents and tool calls. Provider state that must be sent back
on the next turn is dropped:

- OpenAI Responses API: reasoning items. Requests use `store=False`, so they could be
  carried with `include=["reasoning.encrypted_content"]`.
- Gemini 3: `thought_signature` on function call parts. `google_genai` sends the documented
  `skip_thought_signature_validator` bypass instead. Gemini accepts it, but the reasoning
  context is lost between tool calls.
- Anthropic models with thinking always on (Sonnet 5.5, Opus 5.5, Fable 5.1): thinking
  blocks are dropped. The Sonnet 5.5 migration guide says to pass them back unchanged.
  Replayed tool calls without them still passed the shared chat model tests on 2026-10-07.

## To decide

- Where `AIMessage` holds provider-opaque state (for example per content part or per tool
  call), and how other providers ignore state they do not own.
- Then implement it in `openai`, `google_genai`, and `anthropic`.
