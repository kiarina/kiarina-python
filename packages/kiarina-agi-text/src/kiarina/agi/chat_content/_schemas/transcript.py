from dataclasses import dataclass, field
from typing import Any

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

    parts: list[ContentPart] = field(default_factory=list)
    """
    The rest of the conversation in order: a text part for each XML element,
    followed by the media parts it marks with `<attachment index="N" />`.
    """

    @property
    def prompt(self) -> str:
        """The conversation as `<messages>` XML, without the media."""
        texts = [str(part["text"]) for part in self.parts if part["type"] == "text"]
        return "\n".join(["<messages>", *texts, "</messages>"])

    @property
    def media_parts(self) -> list[ContentPart]:
        return [part for part in self.parts if part["type"] != "text"]

    def to_system_prompt(self, *, tools_enabled: bool) -> str:
        """The system messages followed by how to read the transcript."""
        instructions = _FORMAT_INSTRUCTIONS

        if tools_enabled:
            instructions += f" {_TOOL_INSTRUCTIONS}"

        return f"{self.system}\n\n{instructions}" if self.system else instructions

    def to_instruction(self, *, tool_choice: ToolChoice | None = None) -> str:
        """The request to respond, and the tool choice."""
        lines = ["Respond to the last message in <messages>."]

        if tool_choice == "any":
            lines.append("You must respond by calling one of the provided tools.")
        elif tool_choice is not None and tool_choice != "auto":
            lines.append(f"You must respond by calling the `{tool_choice}` tool.")

        return "\n".join(lines)

    def to_user_prompt(self, *, tool_choice: ToolChoice | None = None) -> str:
        """The transcript followed by the instruction, as one text."""
        return f"{self.prompt}\n\n{self.to_instruction(tool_choice=tool_choice)}"

    def to_user_parts(
        self,
        *,
        tool_choice: ToolChoice | None = None,
        cache_control: dict[str, Any] | None = None,
    ) -> list[ContentPart]:
        """
        The transcript as parts, one per element with its media, then the
        instruction.

        `cache_control` marks the last part of the conversation. The next request
        only appends to the conversation, so it starts with the same parts and can
        read the cache. A cache is matched part by part, so one text holding the
        whole conversation would never match.
        """
        parts: list[ContentPart] = [
            {k: v for k, v in part.items() if k != "cache_control"}
            for part in self.parts
        ]
        closing = "</messages>"

        if parts and parts[0]["type"] == "text":
            parts[0] = {**parts[0], "text": f"<messages>\n{parts[0]['text']}"}
        else:
            closing = f"<messages>\n{closing}"

        if parts and cache_control:
            parts[-1] = {**parts[-1], "cache_control": cache_control}

        instruction = self.to_instruction(tool_choice=tool_choice)
        return [*parts, {"type": "text", "text": f"{closing}\n\n{instruction}"}]
