from kiarina.agi.chat_provider import (
    ChatProviderState,
    collect_message_states,
    compute_message_hashes,
)
from kiarina.agi.message import AIMessage, HumanMessage, Message


def _conversation() -> list[Message]:
    """Each AI message carries a state written as its provider would."""
    messages: list[Message] = []

    for name, text in [("anthropic", "A"), ("openai", "B"), ("anthropic", "C")]:
        messages.append(HumanMessage.create(f"Question {text}"))
        ai_message = AIMessage.create(text)
        ChatProviderState(
            name=name,
            history_hash=compute_message_hashes(
                [*messages, ai_message], model_name="m"
            )[-1],
            data={"text": text},
        ).write_to(ai_message)
        messages.append(ai_message)

    return messages


def _texts(messages: list[Message], name: str, model_name: str = "m") -> list[str]:
    states = collect_message_states(messages, name, model_name=model_name)
    return [state.data["text"] for state in states.values()]


def test_collect_message_states() -> None:
    messages = _conversation()

    assert _texts(messages, "anthropic") == ["A", "C"]
    assert _texts(messages, "openai") == ["B"]
    assert _texts(messages, "anthropic", model_name="other") == []


def test_collect_message_states_after_edit() -> None:
    # An edit drops the states after it, and keeps the ones before it.
    messages = _conversation()
    messages[2].contents[0].text = "Edited question"

    assert _texts(messages, "anthropic") == ["A"]
    assert _texts(messages, "openai") == []

    # Removing messages before them (a summary, say) drops them all.
    assert _texts(_conversation()[2:], "anthropic") == []
