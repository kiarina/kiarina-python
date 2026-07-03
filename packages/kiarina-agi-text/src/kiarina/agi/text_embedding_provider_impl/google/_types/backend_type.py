from typing import Literal, TypeAlias

BackendType: TypeAlias = Literal[
    "gemini_api",
    "vertex_ai",
    "vertex_ai_api_key",
]
