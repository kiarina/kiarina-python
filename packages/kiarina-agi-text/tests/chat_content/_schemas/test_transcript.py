import pytest

from kiarina.agi.chat_content import Transcript

_IMAGE = {"type": "image", "source": "x"}


def test_to_system_prompt() -> None:
    assert (
        Transcript()
        .to_system_prompt(tools_enabled=False)
        .startswith("The conversation so far is given in <messages>")
    )

    system_prompt = Transcript(system="Be brief.").to_system_prompt(tools_enabled=True)

    assert system_prompt.startswith("Be brief.\n\nThe conversation so far")
    assert system_prompt.endswith("Never write a tool call as text or XML.")


@pytest.mark.parametrize(
    ("tool_choice", "expected"),
    [
        (None, []),
        ("auto", []),
        ("any", ["You must respond by calling one of the provided tools."]),
        ("search", ["You must respond by calling the `search` tool."]),
    ],
)
def test_to_user_prompt(tool_choice: str | None, expected: list[str]) -> None:
    transcript = Transcript(parts=[{"type": "text", "text": "<a />"}, _IMAGE])

    assert transcript.prompt == "<messages>\n<a />\n</messages>"
    assert transcript.media_parts == [_IMAGE]
    assert transcript.to_user_prompt(tool_choice=tool_choice).splitlines() == [
        "<messages>",
        "<a />",
        "</messages>",
        "",
        "Respond to the last message in <messages>.",
        *expected,
    ]


def test_to_user_parts() -> None:
    transcript = Transcript(
        parts=[
            {"type": "text", "text": "<a />"},
            {"type": "text", "text": "<b />", "cache_control": {"type": "ephemeral"}},
            _IMAGE,
        ]
    )

    parts = transcript.to_user_parts(
        tool_choice="any", cache_control={"type": "ephemeral"}
    )

    assert parts == [
        {"type": "text", "text": "<messages>\n<a />"},
        {"type": "text", "text": "<b />"},
        {**_IMAGE, "cache_control": {"type": "ephemeral"}},
        {
            "type": "text",
            "text": "</messages>\n\nRespond to the last message in <messages>.\n"
            "You must respond by calling one of the provided tools.",
        },
    ]
    assert transcript.parts[1]["cache_control"] == {"type": "ephemeral"}


def test_to_user_parts_empty() -> None:
    assert Transcript().to_user_parts(cache_control={"type": "ephemeral"}) == [
        {
            "type": "text",
            "text": "<messages>\n</messages>\n\nRespond to the last message in <messages>.",
        }
    ]
    assert Transcript(parts=[_IMAGE]).to_user_parts()[0] == _IMAGE
