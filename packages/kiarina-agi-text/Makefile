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

tmp_test:
	KIARINA_AGI_TEXT_TEST_CHAT_MODEL=claude-sonnet-5 \
	mise run test kiarina-agi-text --no-pytest-args --costly --path tests/chat_model/_helpers/
