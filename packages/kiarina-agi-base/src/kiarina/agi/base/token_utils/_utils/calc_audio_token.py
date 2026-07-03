from .._types.token_count import TokenCount


def calc_audio_token(duration: float) -> TokenCount:
    # NOTE: https://ai.google.dev/gemini-api/docs/audio?hl=ja
    return int(32 * duration)
