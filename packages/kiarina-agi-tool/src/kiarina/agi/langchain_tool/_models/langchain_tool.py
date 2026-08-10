from collections.abc import AsyncIterator
from copy import deepcopy
from typing import Any, TypeAlias

from langchain.tools import BaseTool as LCBaseTool
from pydantic import BaseModel

from kiarina.agi.content import Content
from kiarina.agi.event import Event, ToolMessageEvent
from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import Tool, ToolContext
from kiarina.agi.tool_info import ToolInfo, ToolName, create_tool_info
from kiarina.i18n import Language

LCContent: TypeAlias = str | list[str | dict[str, Any]]
Artifact: TypeAlias = dict[str, Any]


class LangChainTool(Tool):
    def __init__(
        self,
        lc_tool: LCBaseTool,
        *,
        raw_output: bool = False,
    ) -> None:
        tool_call_schema = lc_tool.tool_call_schema

        if not isinstance(tool_call_schema, type) or not issubclass(
            tool_call_schema, BaseModel
        ):
            raise ValueError(
                "LangChainTool requires the tool_call_schema to be a Pydantic model class"
            )

        self.lc_tool: LCBaseTool = lc_tool
        self.raw_output: bool = raw_output

        self.name: ToolName = lc_tool.name
        self.tool_schema: type[BaseModel] = tool_call_schema
        self.return_direct: bool = lc_tool.return_direct
        self.accepts_ctx: bool = False

    def to_tool_info(self, language: Language | None = None) -> ToolInfo:
        return create_tool_info(
            self.tool_schema,
            name=self.name,
            description=self.lc_tool.description,
        )

    async def run(self, ctx: ToolContext) -> AsyncIterator[Event]:
        tool_args_model = self.tool_schema(**ctx.tool_call.args)

        tool_args = {
            field_name: getattr(tool_args_model, field_name)
            for field_name in self.tool_schema.model_fields
        }

        output = await self.lc_tool.ainvoke(tool_args)
        lc_content, artifact = _parse_output(output)

        if self.raw_output:
            contents = _to_contents(lc_content)
        else:
            contents = _to_formatted_contents(ctx, lc_content)

        yield ToolMessageEvent(
            message=ToolMessage(
                tool_name=self.name,
                tool_call_args=deepcopy(ctx.tool_call.args),
                tool_call_id=ctx.tool_call.id,
                return_direct=self.return_direct,
                contents=contents,
                artifact=artifact,
            )
        )

    def __str__(self) -> str:
        return self.lc_tool.__class__.__name__


def _parse_output(output: Any) -> tuple[LCContent, Artifact]:
    if isinstance(output, str):
        return output, {}

    if isinstance(output, list):
        return output, {}

    if isinstance(output, tuple):
        if len(output) != 2:  # pragma: no cover
            raise ValueError(
                f"Invalid output format. Expected a tuple of (content, artifact), got: {output}"
            )

        if not isinstance(output[1], dict):
            return output[0], {"data": output[1]}

        return output[0], output[1]

    return str(output), {}


def _to_contents(lc_content: LCContent) -> list[Content]:
    if isinstance(lc_content, str):
        return [Content(text=lc_content)]

    contents: list[Content] = []

    for item in lc_content:
        if isinstance(item, str):
            contents.append(Content(text=item))
        elif isinstance(item, dict):
            if item.get("type") == "text":
                contents.append(Content(text=item.get("text", "")))
            else:
                contents.append(Content(payload=item))
        else:  # pragma: no cover
            raise ValueError(f"Unsupported content type: {type(item)}")

    return contents


def _to_formatted_contents(ctx: ToolContext, lc_content: LCContent) -> list[Content]:
    if not _should_format(lc_content):
        return _to_contents(lc_content)

    if isinstance(lc_content[0], str):
        text = lc_content[0].strip()
    else:
        text = str(lc_content[0].get("text") or "").strip()

    if not text:
        text = "empty output"

    text = f"Tool executed.\n\n{ctx.tool_call.to_text()}\n\n<output>{text}</output>"

    return [Content(text=text)]


def _should_format(lc_content: LCContent) -> bool:
    if isinstance(lc_content, str):
        return True

    if len(lc_content) != 1:
        return False

    if isinstance(lc_content[0], str):
        return True

    if isinstance(lc_content[0], dict) and lc_content[0].get("type") == "text":
        return True

    return False
