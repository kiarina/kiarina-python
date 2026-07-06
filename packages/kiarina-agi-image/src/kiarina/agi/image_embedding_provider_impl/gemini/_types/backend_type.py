from typing import Literal

BackendType = Literal[
    "gemini_api",
    "vertex_ai_api_key",
    "vertex_ai_credentials",
]
"""
Google GenAI backend type

- "gemini_api": Use Gemini API
- "vertex_ai_api_key": Use Vertex AI with API key authentication
- "vertex_ai_credentials": Use Vertex AI with service account authentication
"""
