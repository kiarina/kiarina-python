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

## Next steps

1. With the capture server: does Codex continue the same turn when a held tool call request is
   answered later? Then one live pair: does the resumed request read the cache?
2. Add `BaseMessage.metadata` and the state convention.
3. Implement Codex thread resumption, then carry reasoning state in `openai`, `google_genai`, and
   `anthropic`, and thinking blocks in `claude_agent_sdk`.
