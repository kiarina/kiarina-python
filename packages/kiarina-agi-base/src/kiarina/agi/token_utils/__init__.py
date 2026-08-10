"""
This module provides functionality for estimating the number of tokens.
The exact token count varies depending on the model being used.
"""

from ._helpers.calc_text_token import calc_text_token
from ._settings import TokenUtilsSettings, settings_manager
from ._types.image_size import ImageSize
from ._types.token_count import TokenCount
from ._utils.calc_audio_token import calc_audio_token
from ._utils.calc_image_token import calc_image_token
from ._utils.calc_pdf_token import calc_pdf_token
from ._utils.calc_video_token import calc_video_token

__all__ = [
    # ._helpers
    "calc_text_token",
    # ._settings
    "TokenUtilsSettings",
    "settings_manager",
    # ._types
    "ImageSize",
    "TokenCount",
    # ._utils
    "calc_audio_token",
    "calc_image_token",
    "calc_pdf_token",
    "calc_video_token",
]
