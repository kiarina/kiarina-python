.PHONY: format lint test build clean check
.DEFAULT_GOAL := check

format:
	mise run format
lint:
	mise run lint
test:
	mise run test
build:
	mise run build
clean:
	mise run clean
check:
	mise run format
	mise run lint
	mise run test --coverage

.PHONY: asr_provider_google_test
asr_provider_google_test:
	mise run test --costly --path tests/asr_provider_impl/google

.PHONY: asr_provider_openai_test
asr_provider_openai_test:
	mise run test --costly --path tests/asr_provider_impl/openai

.PHONY: tts_provider_google_test
tts_provider_google_test:
	mise run test --costly --path tests/tts_provider_impl/google

.PHONY: tts_provider_openai_test
tts_provider_openai_test:
	mise run test --costly --path tests/tts_provider_impl/openai
