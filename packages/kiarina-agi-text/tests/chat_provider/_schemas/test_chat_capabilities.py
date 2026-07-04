from typing import Any

from kiarina.agi.chat_provider import ChatCapabilities


def test_default_token_count_limit() -> None:
    assert ChatCapabilities().token_count_limit == 772_000


def test_is_supported(capabilities: Any) -> None:
    assert capabilities.is_supported("image") is True


def test_can_include(capabilities: Any) -> None:
    assert capabilities.can_include("human", "image") is True
    assert capabilities.can_include("tool", "image") is False
    assert capabilities.can_include("ai", "audio") is False


def test_to_string(all_enabled_capabilities: Any) -> None:
    print(all_enabled_capabilities.to_string())
