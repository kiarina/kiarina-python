import locale
import os

from .._types.language import Language
from .._utils.normalize_language_tag import normalize_language_tag


def get_system_language() -> Language:
    """
    Get the system's default language tag.

    This function attempts to detect the system's language preference by checking:
    1. Environment variables (LANG, LC_ALL, LC_MESSAGES, LANGUAGE)
    2. locale.getlocale() as fallback
    3. Returns "en" if detection fails or the system locale is C/POSIX

    Returns:
        BCP 47 language tag (e.g., "en", "ja-JP", "fr-FR")

    Example:
        ```python
        from kiarina.i18n import get_system_language, get_translator

        # Automatically use system language
        language = get_system_language()
        t = get_translator(language, "app.greeting")
        print(t("hello", name="World"))
        ```
    """
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
