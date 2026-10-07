import pytest

from kiarina.agi.chat_content import Transcript


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
        (None, None),
        ("auto", None),
        ("any", "You must respond by calling one of the provided tools."),
        ("search", "You must respond by calling the `search` tool."),
    ],
)
def test_to_user_prompt(tool_choice: str | None, expected: str | None) -> None:
    lines = (
        Transcript(prompt="<messages>\n</messages>")
        .to_user_prompt(tool_choice=tool_choice)
        .splitlines()
    )

    assert lines[:4] == [
        "<messages>",
        "</messages>",
        "",
        "Respond to the last message in <messages>.",
    ]
    assert lines[4:] == ([expected] if expected else [])
