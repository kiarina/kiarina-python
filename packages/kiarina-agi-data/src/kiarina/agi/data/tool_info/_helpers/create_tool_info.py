from typing import Any

from pydantic import BaseModel

from .._models.tool_info import ToolInfo
from .._types.tool_name import ToolName


def create_tool_info(
    source: type[BaseModel] | dict[str, Any],
    name: ToolName | None = None,
    description: str | None = None,
    cache_control: dict[str, Any] | None = None,
) -> ToolInfo:
    if isinstance(source, type):
        if not issubclass(source, BaseModel):
            raise AssertionError("Source must be a Pydantic model class or a dict.")

        args_schema = source.model_json_schema()
    else:
        args_schema = source

    source_title = args_schema.pop("title", None)
    source_name = args_schema.pop("name", None)
    source_description = args_schema.pop("description", None)

    name = name or source_name or source_title

    if not name:  # pragma: no cover
        raise ValueError("Name must be provided if not found in the source.")

    description = description or source_description

    if not description:  # pragma: no cover
        raise ValueError("Description must be provided if not found in the source.")

    return ToolInfo(
        name=name,
        description=description,
        args_schema=args_schema,
        cache_control=cache_control,
    )
