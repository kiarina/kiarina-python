import locale
import os

from .._types.language import Language
from .._utils.normalize_language_tag import normalize_language_tag


def get_system_language() -> Language:
    try:
        for env_var in ("LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE"):
            lang = os.environ.get(env_var)

            if lang:
                return normalize_language_tag(lang)

    except Exception:  # pragma: no cover
        pass

    try:
        current_locale = locale.getlocale()[0]

        if current_locale:
            return normalize_language_tag(current_locale)

    except Exception:  # pragma: no cover
        pass

    return "en"
