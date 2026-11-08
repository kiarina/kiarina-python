# Move to anthropic 2 and google-genai 3

## Background

Both SDKs released a major version that changes the API the requests reach, not only Python
types. `pyproject.toml` keeps `anthropic>=0.84.0,<2` and `google-genai>=1.65.0,<3` until this
is done. Raising the bounds resolves without conflict (checked 2026-11-09: anthropic 2.6.0,
google-genai 3.0.0).

### anthropic 2 (2026-10-21)

The SDK sends `anthropic-version: 2026-10-21`, also from the Vertex client
([migration guide](https://platform.claude.com/docs/en/api/migration-2026-10-21)).

- `temperature`, `top_p`, and `top_k` return `400`, even at their defaults. The `anthropic`
  and `anthropic_vertex` chat providers have a public `temperature` setting, sent through
  `extra_body`. It has to go (breaking for anyone who sets it) or be ignored with a warning.
- `MessageParam` is a union of per-role types; calling it raises `TypeError`.
- `document` blocks in `assistant` messages and `citations` on `text` blocks in `user`
  messages return `400`.
- A client holds one credential (`ValueError` for two).

### google-genai 3 (2026-11-05)

- The Gemini Developer API defaults to `v1` instead of `v1beta`. Vertex AI keeps `v1beta1`.
  Some aliases (`gemini-flash-latest` and similar) exist only on `v1beta`, and preview
  features may not be on `v1`. Either pass `api_version="v1beta"` in `HttpOptions` or check
  every Google provider on `v1`: chat, text embedding, image embedding, image generation,
  video generation, ASR, TTS.
- The HTTP client is `httpx2`; `httpx` is no longer installed by default. Transport
  exceptions caught from the SDK must be `httpx2`'s.
- `tenacity` stays below 9.2 until then (google-genai 2.34.0 requires `tenacity<9.2.0`).

## To do

- Decide what happens to the `temperature` setting of the Anthropic providers (user's call:
  it is a breaking change of a public setting).
- Decide the Gemini API version for the Google providers.
- Update the code and bounds together, then run the costly tests of the affected providers
  with the cheapest model of each provider.
- Record the change in `CHANGELOG.md`; kiari and kiari-plugins follow from kiarina's HEAD.
