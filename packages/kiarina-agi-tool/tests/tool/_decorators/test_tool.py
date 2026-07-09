from pydantic import BaseModel

from kiarina.agi.tool import BaseTool, ToolContext, tool


class AddNumbersSchema(BaseModel):
    """Add two numbers"""

    a: int
    b: int


def test_without_parentheses() -> None:
    @tool
    def HelloTool() -> str:
        """Say hello"""
        return "hello"

    assert issubclass(HelloTool, BaseTool)
    assert HelloTool.__name__ == "HelloTool"
    assert HelloTool.__doc__ == "Say hello"
    assert HelloTool.tool_schema.__doc__ == "Say hello"
    assert HelloTool.return_direct is False
    assert HelloTool.accepts_ctx is False


def test_with_parentheses() -> None:
    @tool()
    def HelloTool() -> str:
        """Say hello"""
        return "hello"

    assert issubclass(HelloTool, BaseTool)
    assert HelloTool.__name__ == "HelloTool"
    assert HelloTool.__doc__ == "Say hello"
    assert HelloTool.tool_schema.__doc__ == "Say hello"
    assert HelloTool.return_direct is False
    assert HelloTool.accepts_ctx is False


def test_with_options() -> None:
    @tool(tool_schema=AddNumbersSchema, return_direct=True)
    def AddNumbersTool(a: int, b: int) -> str:
        return str(a + b)

    assert issubclass(AddNumbersTool, BaseTool)
    assert AddNumbersTool.__name__ == "AddNumbersTool"
    assert AddNumbersTool.__doc__ is None
    assert AddNumbersTool.tool_schema is AddNumbersSchema
    assert AddNumbersTool.return_direct is True
    assert AddNumbersTool.accepts_ctx is False


def test_accepts_ctx() -> None:
    @tool(tool_schema=AddNumbersSchema)
    def AddNumbersTool(ctx: ToolContext, a: int, b: int) -> str:
        return str(a + b)

    assert issubclass(AddNumbersTool, BaseTool)
    assert AddNumbersTool.accepts_ctx is True
