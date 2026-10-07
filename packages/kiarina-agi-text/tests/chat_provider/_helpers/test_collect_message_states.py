from kiarina.agi.chat_provider import (
    ChatProviderState,
    collect_message_states,
    compute_message_hash,
)
from kiarina.agi.message import AIMessage, HumanMessage, Message


def _ai(text: str, name: str, model_name: str) -> AIMessage:
    message = AIMessage.create(text)
    ChatProviderState(
        name=name,
        history_hash=compute_message_hash(message, model_name=model_name),
        data={"text": text},
    ).write_to(message)
    return message


def test_collect_message_states() -> None:
    edited = _ai("Before", "anthropic", "m")
    edited.contents[0].text = "After"

    messages: list[Message] = [
        HumanMessage.create("Hi"),
        _ai("A", "anthropic", "m"),
        _ai("B", "openai", "m"),
        _ai("C", "anthropic", "other"),
        edited,
        _ai("D", "anthropic", "m"),
    ]

    states = collect_message_states(messages, "anthropic", model_name="m")

    assert {index: state.data["text"] for index, state in states.items()} == {
        1: "A",
        5: "D",
    }
