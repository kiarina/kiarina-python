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

.PHONY: video_generation_provider_google_test
video_generation_provider_google_test:
	mise run test --costly --path tests/video_generation_provider_impl/google

.PHONY: video_generation_provider_openai_test
video_generation_provider_openai_test:
	mise run test --costly --path tests/video_generation_provider_impl/openai

.PHONY: video_generation_model_test
video_generation_model_test:
	mise run test --costly --path tests/video_generation_model
