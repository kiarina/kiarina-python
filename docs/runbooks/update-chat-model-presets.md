# Update Chat Model Presets

Procedure for updating the `kiarina-agi-text` chat model presets.

## Scope

The primary files are:

- `packages/kiarina-agi-text/src/kiarina/agi/chat_model/_settings.py`
- `packages/kiarina-agi-text/src/kiarina/agi/chat_model/_types/chat_model_specifier.py`

Change a provider implementation's standalone default model only when explicitly requested. Do not change public APIs or settings schemas solely for a preset update.

## Procedure

### 1. Research official information

Confirm the following from each provider's primary documentation:

- model ID used by the API
- availability and preview, deprecated, or shutdown status
- context window and maximum output tokens
- standard input, cached input, cache write, and output prices
- image, audio, video, and PDF support
- tool calling, built-in tool, and endpoint constraints
- successor models and migration paths

Record the date checked and source URLs in the working notes. Do not rely only on search results or comparison articles; cross-check the provider's model, pricing, deprecation, and migration documentation.

Primary references:

- [OpenAI Models](https://developers.openai.com/api/docs/models)
- [Anthropic Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Gemini Latest Models](https://ai.google.dev/gemini-api/docs/latest-model)
- [Gemini Deprecations](https://ai.google.dev/gemini-api/docs/deprecations)

### 2. Select the preset set

Review the role of existing presets instead of only adding new models.

An older model can be removed when a newer model meets all of these conditions:

- the provider identifies it as the successor or migration target
- its standard price is the same or lower
- its primary performance is the same or better
- it does not lose context, output, modality, or tool capabilities
- it has equivalent or better availability

Keep an older model when it retains a distinct role such as lower price, lower latency, or a unique modality. Do not retain preview, invite-only, or specialized models when a current general-purpose model replaces their unique capability.

Assign aliases only to stable presets intended for normal use. Ensure no alias refers to a removed preset.

### 3. Update settings

Register the model-specific values in `ChatModelSettings.presets`.

| Field | Rule |
| --- | --- |
| `model_name` | Official model ID sent to the API |
| `context_window` | Context limit documented by the provider |
| `max_output_tokens` | Output limit documented by the provider |
| `token_count_limit` | Input limit that reserves output and operational headroom |
| cost fields | Standard prices in microdollars per 1K tokens |
| `input_enabled` | Enable only modalities accepted by the provider |
| `endpoint_type` | Select the endpoint required by the model |
| `vertex_ai_location` | A location where the Vertex AI model is served, such as `global` |
| `visible` | Consider `False` for preview, specialized, or fallback-constrained models |

Multiply `$/MTok` by 1,000 to convert it to microdollars per 1K tokens. For example, `$3/MTok` becomes `3_000`.

Enable settings representing long-context surcharges only when the model actually has an additional charge. Do not enable them when the full context uses standard pricing.

For OpenAI GPT-6 presets, prompts over 272K input tokens apply a 2x input and 1.5x output multiplier to the full request. Cache writes cost 1.25x the uncached input rate. Use input tokens including cache reads and cache writes when evaluating the threshold.

Search for references to removed presets in types and documentation.

```bash
rg 'old-model-name' packages/kiarina-agi-text docs
```

### 4. Do not add settings tests

Do not add tests that only fix the preset values of `ChatModelSettings`. Such tests duplicate the settings values and require both declarations to change for every model update.

Verify API compatibility for new presets through the addition-only API tests. When changing provider logic such as cost calculation, test the provider behavior instead of the settings values.

### 5. Run addition-only API tests

Run the costly chat model helper tests for each new preset only when adding that preset. Do not run them for price-only changes or routine regression tests.

For high-priced presets (such as GPT-6 Astra or Claude Fable), do not run the helper tests. Send one request with a few output tokens to confirm the model ID and settings are accepted, and test behavior with a cheaper model of the same provider and provider path.

```bash
KIARINA_AGI_TEXT_TEST_CHAT_MODEL=<preset-name> \
mise run test kiarina-agi-text --no-pytest-args --costly --path tests/chat_model/_helpers/
```

`--no-pytest-args` ignores the package's entire `.pytest-args` file. This also disables `--reruns`, preventing pointless retries of compatibility errors from newly added models.

When multiple presets are added, run the command separately for every preset. Run them sequentially by default to avoid unnecessary API load and rate limits.

This test covers the invoke, stream, tool calling, parallel tool calling, supported file input, and simulated file output paths.

If credentials are unavailable, resolve authentication separately before evaluating the model settings. Do not treat a pre-authentication failure as a model compatibility result. Never store secrets in the repository or test output.

See [Pytest Markers](../playbooks/pytest-markers.md) for the costly marker and [External Service Tests](../playbooks/external-service-tests.md) for external API tests and authentication.

### 6. Run package and repository checks

After the costly tests, run the regular package tests and repository checks.

```bash
mise run test kiarina-agi-text
make
git diff --check
```

The costly tests are addition-only, but run the regular package tests and `make` for model additions, removals, and price changes.

### 7. Review the final diff

Before completion, confirm that:

- researched values match the configured values
- lower-cost models with a distinct role were not removed accidentally
- deprecated or superseded presets are gone
- every alias resolves to an existing preset
- provider implementation defaults were not changed unintentionally
- public APIs and settings schemas have no unnecessary changes
- addition-only API tests succeeded for every new preset
- package tests and `make` succeeded

## Current Preset Set

Checked on 2026-10-07.

- OpenAI: GPT-6 Astra (top tier), GPT-6.1 Sol (`llm`, `vlm`, and `openai` aliases), and GPT-6 Luna (lowest cost). GPT-6 has no Terra tier, and GPT-6 Luna replaced GPT-5.4 Mini and Nano.
- Anthropic: Claude Sonnet 5.5 (`anthropic` alias), Opus 5.5, Fable 5.1 (hidden), and Haiku 4.5 (lower cost), each also as a hidden `vclaude-*` preset on the `global` location.
- Google: Gemini 3.8 Flash (`google` and `omni` aliases) and Gemini 3.5 Flash-Lite (lower cost). The only newer Pro model is a preview, so it is not a preset.
- local: Qwen3.8-Flash-Next with and without thinking (`local` alias), Qwen3.8-27B, and Qwen3-Omni on kiapi, at zero cost.
- Subscriptions, all hidden, at zero cost: `codex-gpt-6-astra`, `codex-gpt-6.1-sol`, and `codex-gpt-6-luna` (Codex, with Codex's default reasoning effort for each; `codex` alias on GPT-6.1 Sol), then `claude-code-sonnet-5-5`, `claude-code-opus-5-5`, `claude-code-fable-5-1`, and `claude-code-haiku-4-5` (Claude Code; `claude_code` alias on Opus 5.5). They mirror the API presets of the same models. Their context windows are the subscription's, not the API's: Codex's model list gives the GPT-6 models 272K.
- Prices are list prices. Temporary promotional prices are not used.
