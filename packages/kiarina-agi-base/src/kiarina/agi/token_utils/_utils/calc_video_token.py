from .._types.token_count import TokenCount


def calc_video_token(duration: float) -> TokenCount:
    # NOTE: https://ai.google.dev/gemini-api/docs/video-understanding?hl=ja
    return int(300 * duration)
