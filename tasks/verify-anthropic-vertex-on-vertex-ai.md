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
