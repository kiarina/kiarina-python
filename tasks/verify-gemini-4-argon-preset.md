# Verify the gemini-4-argon preset

Done when: the addition-only helper tests pass for `gemini-4-argon`, or its settings are fixed so they do.

## Background

`gemini-4-argon` was added on 2026-10-28 from the official model and pricing pages (1,048,576 context, 65,536 output, regular prices $4 / $0.20 cached / $20, implicit caching only, input text, image, audio, video, and PDF).
Its helper tests could not run: the Gemini API returned `402 RESOURCE_EXHAUSTED` ("Your prepayment credits are depleted") for every call, so nothing about the model was checked. `gemini-3.8-flash` got the same error, so it is the account, not the model.

## To do

- After the prepayment credits are topped up in AI Studio (the owner's step), run:
  `KIARINA_AGI_TEXT_TEST_CHAT_MODEL=gemini-4-argon mise run test kiarina-agi-text --no-pytest-args --costly --path tests/chat_model/_helpers/`
- Watch for: explicit context caching is not supported on Argon (the provider uses implicit caching only today), and long outputs past 65,536 tokens need its long-decode mode, which the provider does not use.
