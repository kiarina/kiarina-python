import tiktoken

from .._settings import settings_manager
from .._types.token_count import TokenCount


def calc_text_token(text: str) -> TokenCount:
    settings = settings_manager.get_settings()
    encoding = tiktoken.encoding_for_model(settings.tiktoken_model_name)
    return len(encoding.encode(text))
