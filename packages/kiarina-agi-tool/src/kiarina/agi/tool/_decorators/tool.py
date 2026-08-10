import inspect
from collections.abc import Callable
from typing import Any, overload

from pydantic import BaseModel, create_model

from .._models.base_tool import BaseTool
from .._types.tool_output_like import ToolOutputLike


@overload
def tool(func: Callable[..., ToolOutputLike]) -> type[BaseTool]: ...


@overload
def tool(
    *,
    tool_schema: type[BaseModel] | None = None,
    return_direct: bool = False,
) -> Callable[[Callable[..., ToolOutputLike]], type[BaseTool]]: ...


def tool(
    func: Callable[..., ToolOutputLike] | None = None,
    *,
    tool_schema: type[BaseModel] | None = None,
    return_direct: bool = False,
) -> type[BaseTool] | Callable[[Callable[..., ToolOutputLike]], type[BaseTool]]:
    def _create_tool_class(func: Callable[..., ToolOutputLike]) -> type[BaseTool]:
        signature = inspect.signature(func)
        params = signature.parameters
        accepts_ctx = False

        if params:
            first_param = next(iter(params.values()))
            accepts_ctx = (
                first_param.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
                and first_param.name == "ctx"
            )

        class ToolClass(BaseTool):
            def _run(self, *args: Any, **kwargs: Any) -> ToolOutputLike:
                return func(*args, **kwargs)

        ToolClass.__name__ = func.__name__
        ToolClass.__qualname__ = func.__qualname__
        ToolClass.__module__ = func.__module__
        ToolClass.__doc__ = func.__doc__
        ToolClass.tool_schema = _create_tool_schema(func, tool_schema)
        ToolClass.return_direct = return_direct
        ToolClass.accepts_ctx = accepts_ctx

        return ToolClass

    if func is not None:
        return _create_tool_class(func)

    return _create_tool_class


def _create_tool_schema(
    func: Callable[..., ToolOutputLike],
    tool_schema: type[BaseModel] | None,
) -> type[BaseModel]:
    if tool_schema is not None:
        return tool_schema

    schema = create_model(
        f"{func.__name__}Schema",
        __base__=BaseModel,
    )
    schema.__doc__ = func.__doc__

    return schema
