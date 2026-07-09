import inspect
import textwrap
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any, cast

from pydantic import BaseModel, Field, create_model

from kiarina.agi.event import Event
from kiarina.agi.tool_info import ToolInfo, ToolName, create_tool_info
from kiarina.i18n import I18n, Language
from kiarina.i18n_pydantic import translate_pydantic_model

from .._operations.get_additional_fields import get_additional_fields
from .._operations.output_to_event import output_to_event
from .._schemas.tool_context import ToolContext
from .._types.tool import Tool
from .._types.tool_output import ToolOutput
from .._types.tool_output_like import ToolOutputLike


class BaseTool(Tool, ABC):
    tool_schema: type[BaseModel]
    return_direct: bool = False
    accepts_ctx: bool = False

    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: ToolName | None = None

    @property
    def name(self) -> ToolName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Tool name not set")

        return self._name

    @name.setter
    def name(self, value: ToolName) -> None:
        self._name = value

    def to_tool_info(self, language: Language | None = None) -> ToolInfo:
        tool_schema = self.tool_schema

        if language and issubclass(self.tool_schema, I18n):
            tool_schema = translate_pydantic_model(self.tool_schema, language)

        description = _get_docstring(tool_schema)

        if additional_fields := _get_additional_fields(
            self.name, set(tool_schema.model_fields.keys()), language
        ):
            tool_schema = create_model(
                tool_schema.__name__,
                __base__=tool_schema,
                **additional_fields,
            )

        return create_tool_info(
            tool_schema,
            name=self.name,
            description=description,
        )

    async def run(self, ctx: ToolContext) -> AsyncIterator[Event]:
        run_args = [ctx] if self.accepts_ctx else []

        run_kwargs: dict[str, Any] = {**self.init_kwargs, **ctx.tool_call.args}
        run_kwargs = _remove_additional_fields(run_kwargs, self.name)
        run_kwargs = _validate_tool_call_args(run_kwargs, self.tool_schema)

        result = self._run(*run_args, **run_kwargs)

        if inspect.isasyncgen(result):
            async for output in result:
                yield output_to_event(ctx, self, output)
        elif inspect.isawaitable(result):
            yield output_to_event(ctx, self, await result)
        else:
            yield output_to_event(ctx, self, cast(ToolOutput, result))

    @abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> ToolOutputLike: ...

    def __str__(self) -> str:
        return self.__class__.__name__


# --------------------------------------------------
# Tool Info Utilities
# --------------------------------------------------


def _get_docstring(tool_schema: type[BaseModel]) -> str:
    if not (doc := tool_schema.__doc__):  # pragma: no cover
        raise ValueError("tool_schema.__doc__ is required.")

    doc = textwrap.dedent(doc).strip()

    if not doc:  # pragma: no cover
        raise ValueError("tool_schema.__doc__ is required.")

    return doc


def _get_additional_fields(
    tool_name: ToolName,
    existing_field_names: set[str],
    language: Language | None = None,
) -> dict[str, Any]:
    additional_fields: dict[str, Any] = {}

    for field_config in get_additional_fields(tool_name):
        if field_config.name in existing_field_names:
            continue

        additional_fields[field_config.name] = (
            field_config.type,
            Field(description=field_config.get_description(language)),
        )

    return additional_fields


# --------------------------------------------------
# Run Utilities
# --------------------------------------------------


def _remove_additional_fields(
    tool_call_args: dict[str, Any],
    tool_name: ToolName,
) -> dict[str, Any]:
    additional_field_names = {field.name for field in get_additional_fields(tool_name)}
    return {k: v for k, v in tool_call_args.items() if k not in additional_field_names}


def _validate_tool_call_args(
    tool_call_args: dict[str, Any],
    tool_schema: type[BaseModel],
) -> dict[str, Any]:
    model = tool_schema(**tool_call_args)

    return {
        field_name: getattr(model, field_name)
        for field_name in tool_schema.model_fields
    }
