# mypy: ignore-errors

from kiarina.agi.chat_provider_impl.mock import (
    MockChatProvider,
    create_mock_chat_provider,
)


def test_create_mock_chat_provider():
    provider = create_mock_chat_provider(simulate_delay=False)
    assert isinstance(provider, MockChatProvider)
    assert not provider.settings.simulate_delay
