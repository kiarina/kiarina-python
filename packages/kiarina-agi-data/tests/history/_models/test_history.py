import pytest

from kiarina.agi.embedding import Embedding
from kiarina.agi.event import AIMessageEvent, HumanMessageEvent, ToolMessageEvent
from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.history import History
from kiarina.agi.message import HumanMessage, ToolCall
from kiarina.agi.tool_info import ToolInfo


@pytest.fixture
def history() -> History:
    return History()


def test_clear(text_file_info: TextFileInfo) -> None:
    history = History(
        events=[HumanMessageEvent.create("Hello")],
        file_infos=[text_file_info],
        metadata={"key": "value"},
    )
    history.clear()
    assert len(history.events) == 0
    assert len(history.file_infos) == 0
    assert len(history.metadata) == 0


# --------------------------------------------------
# Event Management
# --------------------------------------------------


def test_get_last_event() -> None:
    history = History(
        events=[
            HumanMessageEvent.create("first"),
            HumanMessageEvent.create("second"),
        ]
    )

    event = history.get_last_event("human_message")

    assert event is not None
    assert event.type == "human_message"
    assert event.message.to_text() == "second"


def test_add_event(history: History, text_file_info: TextFileInfo) -> None:
    history.add_event(HumanMessageEvent.create("Hello", [text_file_info]))
    assert len(history.events) == 1
    assert len(history.file_infos) == 1


def test_replace_event() -> None:
    target = HumanMessageEvent.create("before")
    history = History(events=[target])

    history.replace_event(target, HumanMessageEvent.create("after"))

    assert len(history.events) == 1
    assert history.events[0].type == "human_message"
    assert history.events[0].message.to_text() == "after"


def test_replace_event_not_found() -> None:
    history = History(events=[HumanMessageEvent.create("before")])

    with pytest.raises(ValueError, match="Target event not found in history"):
        history.replace_event(
            HumanMessageEvent.create("missing"),
            HumanMessageEvent.create("after"),
        )


# --------------------------------------------------
# Message Management
# --------------------------------------------------


def test_get_last_message() -> None:
    history = History(
        events=[
            HumanMessageEvent.create("first"),
            AIMessageEvent.create("ai"),
            HumanMessageEvent.create("second"),
        ],
    )

    message = history.get_last_message("human")

    assert message is not None
    assert message.to_text() == "second"


def test_get_messages() -> None:
    history = History(
        events=[
            HumanMessageEvent.create("Hello"),
            AIMessageEvent.create("Hello", tool_calls=[ToolCall(id="1", name="tool1")]),
            ToolMessageEvent.create(
                "Tool response", tool_name="tool1", tool_call_id="1"
            ),
        ],
    )

    assert len(history.get_messages()) == 3


def test_add_message(history: History) -> None:
    history.add_message(HumanMessage.create("Hello"))
    assert len(history.events) == 1


# --------------------------------------------------
# File Info Management
# --------------------------------------------------


def test_get_file_info(text_file_info: TextFileInfo) -> None:
    text_file_info.unique_key = "u1"
    history = History(file_infos=[text_file_info])

    assert history.get_file_info(unique_key="u1") == text_file_info


def test_get_file_infos(text_file_info: TextFileInfo) -> None:
    history = History(file_infos=[text_file_info, text_file_info])
    assert len(history.get_file_infos()) == 2


def test_get_file_infos_uri_or_file_path(text_file_info: TextFileInfo) -> None:
    history = History(file_infos=[text_file_info])
    assert (
        len(history.get_file_infos(uri_or_file_path=text_file_info.uri_or_file_path))
        == 1
    )


def test_get_file_infos_group(text_file_info: TextFileInfo) -> None:
    text_file_info.group = "g1"
    history = History(file_infos=[text_file_info])
    assert len(history.get_file_infos(group="g1")) == 1


def test_get_file_infos_no_group(text_file_info: TextFileInfo) -> None:
    text_file_info2 = text_file_info.model_copy(update={"group": "g1"})
    history = History(file_infos=[text_file_info, text_file_info2])
    assert len(history.get_file_infos(no_group=True)) == 1


def test_get_file_infos_no_unique_key(text_file_info: TextFileInfo) -> None:
    text_file_info.unique_key = "u1"
    history = History(file_infos=[text_file_info])
    assert len(history.get_file_infos(no_unique_key=True)) == 0


def test_get_file_infos_ignore_unique_keys(text_file_info: TextFileInfo) -> None:
    text_file_info.unique_key = "u1"
    history = History(file_infos=[text_file_info])
    assert len(history.get_file_infos(ignore_unique_keys=["u1"])) == 0


def test_get_file_infos_in_message(
    history: History, text_file_info: TextFileInfo
) -> None:
    history.add_event(HumanMessageEvent.create("Hello", [text_file_info]))
    assert len(history.get_file_infos(in_message=True)) == 1
    assert len(history.get_file_infos(in_message=False)) == 0


def test_add_file_info(history: History, text_file_info: TextFileInfo) -> None:
    history.add_file_info(text_file_info)

    assert len(history.file_infos) == 1
    assert history.file_infos[0] == text_file_info


def test_remove_file_info(history: History, text_file_info: TextFileInfo) -> None:
    history.add_file_info(text_file_info)

    history.remove_file_info(text_file_info.id)

    assert len(history.file_infos) == 0


# --------------------------------------------------
# Tool Info Management
# --------------------------------------------------


def test_get_tool_info() -> None:
    tool_info = ToolInfo(name="tool1", description="first tool")
    history = History(tool_infos=[tool_info])

    assert history.get_tool_info(name="tool1") == tool_info


def test_get_tool_infos() -> None:
    history = History(
        tool_infos=[
            ToolInfo(name="tool1", description="first tool"),
            ToolInfo(name="tool2", description="second tool", state="inactive"),
        ]
    )

    assert len(history.get_tool_infos()) == 2


def test_get_tool_infos_state() -> None:
    history = History(
        tool_infos=[
            ToolInfo(name="tool1", description="first tool", state="active"),
            ToolInfo(name="tool2", description="second tool", state="inactive"),
            ToolInfo(name="tool3", description="third tool", state="disabled"),
        ]
    )

    assert [tool_info.name for tool_info in history.get_tool_infos(state="active")] == [
        "tool1"
    ]
    assert [
        tool_info.name for tool_info in history.get_tool_infos(state="inactive")
    ] == ["tool2"]
    assert [
        tool_info.name for tool_info in history.get_tool_infos(state="disabled")
    ] == ["tool3"]


def test_add_tool_info(history: History) -> None:
    tool_info = ToolInfo(name="tool1", description="first tool")

    history.add_tool_info(tool_info)
    assert len(history.tool_infos) == 1
    assert history.tool_infos[0] == tool_info

    history.add_tool_info(tool_info)  # duplicate name
    assert len(history.tool_infos) == 1
    assert history.tool_infos[0] == tool_info


def test_remove_tool_info(history: History) -> None:
    tool_info = ToolInfo(name="tool1", description="first tool")
    history.add_tool_info(tool_info)

    history.remove_tool_info("tool1")

    assert len(history.tool_infos) == 0


# --------------------------------------------------
# Embedding Management
# --------------------------------------------------


def test_get_embedding() -> None:
    embedding = Embedding(id="e1", kind="text", space_id="s1", vector=[0.1, 0.2, 0.3])
    history = History(embeddings={"e1": embedding})

    assert history.get_embedding("e1") == embedding


def test_add_embedding(history: History) -> None:
    embedding = Embedding(id="e1", kind="text", space_id="s1", vector=[0.1, 0.2, 0.3])
    history.add_embedding(embedding)

    assert len(history.embeddings) == 1
    assert history.embeddings["e1"] == embedding


def test_remove_embedding(history: History) -> None:
    embedding = Embedding(id="e1", kind="text", space_id="s1", vector=[0.1, 0.2, 0.3])
    history.add_embedding(embedding)

    history.remove_embedding("e1")

    assert len(history.embeddings) == 0


def test_get_embeddings(history: History) -> None:
    embedding1 = Embedding(id="e1", kind="text", space_id="s1", vector=[0.1, 0.2, 0.3])
    embedding2 = Embedding(id="e2", kind="image", space_id="s1", vector=[0.4, 0.5, 0.6])
    embedding3 = Embedding(id="e3", kind="text", space_id="s2", vector=[0.7, 0.8, 0.9])
    history.add_embedding(embedding1)
    history.add_embedding(embedding2)
    history.add_embedding(embedding3)

    assert len(history.get_embeddings()) == 3
    assert len(history.get_embeddings(kind="text")) == 2
    assert len(history.get_embeddings(space_id="s1")) == 2
