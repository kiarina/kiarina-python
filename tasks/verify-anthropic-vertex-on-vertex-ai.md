# Verify anthropic_vertex against Vertex AI

## Background

`anthropic_vertex` is checked by unit tests and by `test_relay_to_anthropic_api`, which relays
the SDK's Vertex requests to the Anthropic API. It has not run against Vertex AI itself.

On 2026-10-07 the Claude models were enabled in the `blazeworks` project, but its Claude
quota is 0 (`429` on every call and on count-tokens). New projects cannot request an
increase until they have usage history.

## To do

- When calls go through, run `make chat_provider_anthropic_vertex_test` with
  `kiarina.lib.google` settings in
  `tests/chat_provider_impl/anthropic_vertex/test_settings.yaml`.
- The Claude 5 series is served only from `global`, `us`, and `eu` on Vertex AI.
- `vclaude-haiku-5-5` (added 2026-10-28) is not verified either: its addition-only helper tests
  got `429` for `global_online_prediction_requests_per_base_model` (base model
  `anthropic-claude-haiku`). Run them when the quota allows:
  `KIARINA_AGI_TEXT_TEST_CHAT_MODEL=vclaude-haiku-5-5 mise run test kiarina-agi-text --no-pytest-args --costly --path tests/chat_model/_helpers/`.
  Set `KIARINA_AGI_CHAT_PROVIDER_IMPL_ANTHROPIC_VERTEX_MAX_RETRY_COUNT=0` first, or the
  retries on `429` keep a run going for many minutes.
