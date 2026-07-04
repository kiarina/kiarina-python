.PHONY: format lint test build clean check \
	chat_provider_lc_anthropic_test \
	chat_provider_lc_anthropic_vertex_test \
	chat_provider_lc_google_genai_test \
	chat_provider_lc_openai_test \
	text_embedding_provider_google_test \
	text_embedding_provider_openai_test
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

chat_provider_lc_anthropic_test:
	mise run test --costly --path tests/chat_provider_impl/lc_anthropic
chat_provider_lc_anthropic_vertex_test:
	mise run test --costly --path tests/chat_provider_impl/lc_anthropic_vertex
chat_provider_lc_google_genai_test:
	mise run test --costly --path tests/chat_provider_impl/lc_google_genai
chat_provider_lc_openai_test:
	mise run test --costly --path tests/chat_provider_impl/lc_openai
text_embedding_provider_google_test:
	mise run test --costly --path tests/text_embedding_provider_impl/google
text_embedding_provider_openai_test:
	mise run test --costly --path tests/text_embedding_provider_impl/openai
