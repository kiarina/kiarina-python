# Carry provider state across turns

## Background

`AIMessage` keeps only text contents and tool calls. Provider state that would help the next turn
is dropped:

- OpenAI Responses API: reasoning items. Requests use `store=False`, so they could be
  carried with `include=["reasoning.encrypted_content"]`.
- Gemini 3: `thought_signature` on function call parts. `google_genai` sends the documented
  `skip_thought_signature_validator` bypass instead. Gemini accepts it, but the reasoning
  context is lost between tool calls.
- Anthropic models with thinking always on (Sonnet 5.5, Opus 5.5, Fable 5.1): thinking
  blocks are dropped. The Sonnet 5.5 migration guide says to pass them back unchanged.
  Replayed tool calls without them still passed the shared chat model tests on 2026-10-07.
- `codex_app_server`: each request starts a new thread, and Codex reads no prompt cache across
  threads (measured 2026-10-07, see `docs/concepts/chat-providers.md`). Within one thread the
  cache works. Keeping the thread would also skip the few seconds of startup.

## Agreed design (2026-10-08, with kiarina)

- Move `ToolMessage.metadata: dict[str, Any]` up to `BaseMessage.metadata`. kiarina-agi-data only
  knows a free dict on every message, so it does not depend on chat providers.
- A chat provider keeps its state under one key, for example
  `metadata["chat_provider"] = {"name": "codex_app_server", "history_hash": ..., ...}`. Only
  kiarina-agi-text knows the key. Other providers ignore state with another name, and display code
  (kiari, the console tool logger) skips the key, because values such as encrypted reasoning can be
  large.
- Metadata is never sent to a model: not in text conversion, token estimates, or transcripts.
- `history_hash` is the hash of the history up to that AI turn, as the provider sends it (Responses
  items for Codex, transcript blocks for Claude Code). If kiarina rewrites the history (file
  shrinking, summaries, edits), the hash no longer matches and the provider starts fresh. State is
  only an optimization; correctness never depends on it.
- Only the final `AIMessage` of a stream carries the state, not the chunks.

## Codex thread resumption (plan)

1. When returning tool calls, keep the app-server process and its paused turn alive, with the tool
   call request unanswered, and put the thread id and history hash in the state.
2. When the next request is the previous history plus the results of those tool calls, answer the
   held request with the results. Codex continues the same turn and sends its next model request.
3. When a new human message comes after the turn completed, start a new turn on the same thread.
4. Otherwise start a new thread, as today.

Open points: how long a paused process lives, how many live at once, two requests for one thread
at the same time, and cleanup on exit. After a restart the state is still in the saved history but
the process is gone, so the provider starts fresh.

## Findings (2026-10-08)

- Capture server: a tool call request held for 3 seconds sent nothing to the model. Answering it
  later continued the same turn (the next request carried the function call outputs and the same
  `prompt_cache_key`), and a later `turn/start` with a new message continued the same thread.
- Live, GPT-6.1 Sol, the model calls a tool, the request is held 5 seconds, then answered:

  | History | New thread each time | Same thread, resumed |
  | --- | --- | --- |
  | 3.3K tokens | 0 read | 0 read |
  | 12K tokens | 0 read | 11,520 read |

  So resuming makes the cache work, above a size somewhere between 3.3K and 12K tokens. Codex
  reports `cacheWriteInputTokens` as 0 even when the next request reads the cache.
- On the live server the tool call request (`item/tool/call`) arrives before `rawResponse/completed`,
  so resumption must remember requests seen before the response ends. The capture server sends
  them in the other order.
- Injected items are echoed as `rawResponseItem/completed` with `turnId: "auto-compact-0"`, which
  the provider already skips by matching its own turn id.

## Progress

- 2026-10-08: `BaseMessage.metadata` (moved up from `ToolMessage`) and `ChatProviderState`,
  `find_chat_provider_state`, `compute_history_hash` in `kiarina.agi.chat_provider`. The
  convention is in `docs/concepts/chat-providers.md` ("Provider State"). No provider uses it yet.
  kiari saves `History` as pydantic models, so metadata is saved and restored without changes;
  its tool message renderer prints tool metadata only.
- On release: raise kiarina-agi-text's `kiarina-agi-data` floor (now `>=2.6.0`) to the release
  that has `BaseMessage.metadata`, because `ChatProviderState` reads metadata from AI messages.

- 2026-10-08: Codex thread resumption in `codex_app_server` (`thread_reuse`, default on). Kept
  threads live in `live_thread_pool`; a paused turn gets tool results as replies, a completed turn
  gets the new messages and a new turn, anything else starts a new thread. Live, 12K history:
  4.2 s and 0 cached, then the resumed request 2.5 s and 11,392 cached, then the next turn 11,520
  cached. The changes stayed inside `codex_app_server` (and its tests).

## Next steps

1. Carry reasoning state in `openai` (encrypted reasoning items), `google_genai` (thought
   signatures), and `anthropic` (thinking blocks), and thinking blocks in `claude_agent_sdk`.
