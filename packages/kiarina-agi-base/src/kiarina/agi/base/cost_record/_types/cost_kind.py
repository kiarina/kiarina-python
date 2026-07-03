from typing import Literal

CostKind = (
    Literal[
        "asr",
        "chat",
        "deep_research",
        "image",
        "text_embedding",
        "image_embedding",
        "tts",
        "video",
        "web_search",
    ]
    | str
)
