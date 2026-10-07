from dataclasses import dataclass, field

from kiarina.agi.tool_info import ToolChoice

from .._types.content_part import ContentPart

_FORMAT_INSTRUCTIONS = (
    "The conversation so far is given in <messages> as XML. "
    "human_message is the user, ai_message is you, tool_call and tool_result are "
    "the tools you called and their results, and system_message is an instruction "
    'from the system. <attachment index="N" /> marks the Nth attached file. '
    "Continue the conversation as the assistant by responding to the last message."
)

_TOOL_INSTRUCTIONS = (
    "When an action is needed, call the provided tools. "
    "Never write a tool call as text or XML."
)


@dataclass
class Transcript:
    """A conversation flattened into one prompt, for runtimes that take a single turn."""

    system: str | None = None
    """The leading system messages."""

    prompt: str = ""
    """The rest of the conversation as `<messages>` XML."""

    media_parts: list[ContentPart] = field(default_factory=list)
    """Media to attach after the prompt. `<attachment index="N" />` in the prompt marks each."""

    def to_system_prompt(self, *, tools_enabled: bool) -> str:
        """The system messages followed by how to read the transcript."""
        instructions = _FORMAT_INSTRUCTIONS

        if tools_enabled:
            instructions += f" {_TOOL_INSTRUCTIONS}"

        return f"{self.system}\n\n{instructions}" if self.system else instructions

    def to_user_prompt(self, *, tool_choice: ToolChoice | None = None) -> str:
        """The transcript followed by the request to respond, and the tool choice."""
        lines = [self.prompt, "", "Respond to the last message in <messages>."]

        if tool_choice == "any":
            lines.append("You must respond by calling one of the provided tools.")
        elif tool_choice is not None and tool_choice != "auto":
            lines.append(f"You must respond by calling the `{tool_choice}` tool.")

        return "\n".join(lines)
