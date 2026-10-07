# Make structured output reliable on models without forced tool choice

## Background

`kiarina-agi-runner` structured output (`generate_model`, `generate_dict`, `select_option`)
forces a tool call with `tool_choice="any"` and reads the value from the tool arguments.

Claude Sonnet 5.5, Opus 5.5, and Fable 5.1 reject forced tool choice with a 400, and the
Anthropic API has no replacement that guarantees a tool call. The `anthropic` provider falls
back to `auto` and asks for a tool call in the last user turn
(`append_tool_choice_instruction`). The model usually complies, but nothing guarantees it.

Anthropic's documented options (checked 2026-10-07):

- JSON outputs: `output_config.format` with a `json_schema` makes the whole response match the
  schema. Supported on Sonnet 5.5, Opus 5.5, and Fable 5.1.
- Strict tools: `strict: true` guarantees that a tool call's input matches the schema, not that
  a tool is called. It supports a subset of JSON Schema and needs
  `additionalProperties: false` on every object.

Sources: https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide (Forced tool use
is not supported), https://platform.claude.com/docs/en/build-with-claude/structured-outputs

## To do

- Design how a caller asks for a response format (for example a JSON schema in `ChatOptions`),
  and how each provider maps it: Anthropic `output_config.format`, OpenAI and Gemini
  structured outputs.
- Switch structured output in `kiarina-agi-runner` to it where the model supports it, and keep
  the tool-call path for the rest.
- Decide whether to send `strict: true` for structured output tools, given the JSON Schema
  limits.
