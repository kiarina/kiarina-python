import locale
import logging
import os
import shutil
import threading

logger = logging.getLogger(__name__)

_auto_use_nkf: bool | None = None

_auto_use_nkf_lock = threading.Lock()


def should_use_nkf() -> bool:
    global _auto_use_nkf

    with _auto_use_nkf_lock:
        if _auto_use_nkf is not None:
            return _auto_use_nkf

    is_japanese = _is_japanese_environment()
    nkf_available = _is_nkf_available()

    result = is_japanese and nkf_available

    with _auto_use_nkf_lock:
        _auto_use_nkf = result

    logger.debug(
        f"nkf auto-detection: "
        f"Japanese environment={is_japanese}, "
        f"nkf available={nkf_available}, "
        f"result={result}"
    )

    return result


def clear_nkf_cache() -> None:
    global _auto_use_nkf

    with _auto_use_nkf_lock:
        _auto_use_nkf = None

    logger.debug("Cleared nkf determination cache")


def _is_japanese_environment() -> bool:
    try:
        current_locale = locale.getlocale()

        if current_locale[0] and "ja" in current_locale[0].lower():
            return True

        lang_vars = ["LANG", "LC_ALL", "LC_CTYPE"]

        for var in lang_vars:
            value = os.environ.get(var, "")
            if "ja" in value.lower():
                return True

    except Exception as e:
        logger.debug(f"Failed to determine Japanese environment: {e}")

    return False


def _is_nkf_available() -> bool:
    return shutil.which("nkf") is not None
