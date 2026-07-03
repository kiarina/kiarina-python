from typing import Any, NotRequired, TypedDict


class LCToolInfo(TypedDict):
    """
    Type representing information about a tool that can be executed by an LLM

    This format is compatible with the OpenAI function calling specification.

    Example:
    >>> tool_info = {
    >>>     'name': 'hello',
    >>>     'description': 'Say hello to the user',
    >>>     'parameters': {
    >>>         'properties': {'name': {'description': 'User name', 'type': 'string'}},
    >>>         'required': ['name'],
    >>>         'type': 'object'
    >>>     }
    >>> }

    Minimum required fields example:
    >>> tool_info = {
    >>>     'name': 'noop',
    >>>     'description': 'No operation tool',
    >>> }

    Example of generating from a Pydantic model format JSON schema:
    >>> from langchain_core.utils.function_calling import convert_to_openai_function
    >>>
    >>> pydantic_json_schema = {
    >>>     'title': 'Hello',
    >>>     'description': 'Say hello to the user',
    >>>     'type': 'object',
    >>>     'properties': {
    >>>         'name': {
    >>>             'title': 'Name',
    >>>             'type': 'string',
    >>>             'description': 'User name'
    >>>         }
    >>>     },
    >>>     'required': ['name']
    >>> }
    >>>
    >>> tool_info = convert_to_openai_function(pydantic_json_schema)

    Example of generating from a Pydantic model:
    >>> from langchain_core.utils.function_calling import convert_to_openai_function
    >>> from pydantic import BaseModel, Field
    >>>
    >>> class Hello(BaseModel):
    >>>     '''Say hello to the user'''
    >>>     name: str = Field(..., description="User name")
    >>>
    >>> tool_info = convert_to_openai_function(Hello)

    Example of generating from a LangChain Tool class:
    >>> from langchain_core.utils.function_calling import convert_to_openai_function
    >>> from langchain.tools import tool
    >>> from pydantic import BaseModel, Field
    >>>
    >>> class ArgsSchema(BaseModel):
    >>>     name: str = Field(..., description="User name")
    >>>
    >>> @tool(args_schema=ArgsSchema)
    >>> def hello(name: str) -> str:
    >>>     '''Say hello to the user'''
    >>>     return f"Hello, {name}!"
    >>>
    >>> tool_info = convert_to_openai_function(hello)
    """

    name: str
    """Tool name"""

    description: str
    """Tool description"""

    parameters: dict[str, Any]
    """
    Tool parameters schema in JSON Schema format

    If no parameters exist, it will be `{"type": "object", "properties": {}}`.
    """

    cache_control: NotRequired[dict[str, Any]]
    """
    Cache control information for the tool

    Example of setting Anthropic cache:
    >>> tool_info['cache_control'] = {"type": "ephemeral"}
    >>> tool_info['cache_control'] = {"type": "ephemeral", "ttl": "1h"}
    """
