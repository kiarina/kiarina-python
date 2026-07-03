# mypy: ignore-errors

from kiarina.agi.chat_provider_impl.lc_anthropic_vertex import (
    create_lc_anthropic_vertex_chat_provider,
)


def test_create_lc_anthropic_vertex_chat_provider():
    provider = create_lc_anthropic_vertex_chat_provider(temperature=0.7)
    assert provider.settings.temperature == 0.7
