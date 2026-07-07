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

.PHONY: image_generation_provider_google_test
image_generation_provider_google_test:
	mise run test --costly --path tests/image_generation_provider_impl/google

.PHONY: image_generation_provider_openai_test
image_generation_provider_openai_test:
	mise run test --costly --path tests/image_generation_provider_impl/openai

.PHONY: image_generation_model_test
image_generation_model_test:
	mise run test --costly --path tests/image_generation_model

.PHONY: image_embedding_provider_gemini_test
image_embedding_provider_gemini_test:
	mise run test --costly --path tests/image_embedding_provider_impl/gemini
