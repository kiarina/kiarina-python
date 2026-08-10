import re

from .._types.language import Language

_LANGUAGE_RE = re.compile(r"^[a-z]{2,3}$")
_SCRIPT_RE = re.compile(r"^[A-Z][a-z]{3}$")
_REGION_RE = re.compile(r"^(?:[A-Z]{2}|[0-9]{3})$")
_VARIANT_RE = re.compile(r"^(?:[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3})$")


def normalize_language_tag(language: str) -> Language:
    normalized = _strip_locale_suffixes(language.strip())

    if normalized in {"C", "POSIX"}:
        return "en"

    normalized = normalized.replace("_", "-")
    parts = [part for part in normalized.split("-") if part]

    if not parts:
        raise ValueError("Language tag is empty")

    normalized_parts: list[str] = [parts[0].lower()]
    remaining = parts[1:]

    if remaining and len(remaining[0]) == 4 and remaining[0].isalpha():
        normalized_parts.append(remaining.pop(0).title())

    if remaining and (
        (len(remaining[0]) == 2 and remaining[0].isalpha())
        or (len(remaining[0]) == 3 and remaining[0].isdigit())
    ):
        normalized_parts.append(remaining.pop(0).upper())

    normalized_parts.extend(part.lower() for part in remaining)
    language_tag = "-".join(normalized_parts)

    if not _is_normalized_language_tag(language_tag):
        raise ValueError(f"Invalid language tag: {language}")

    return language_tag


def _is_normalized_language_tag(language: str) -> bool:
    parts = language.split("-")

    if not parts or not _LANGUAGE_RE.fullmatch(parts[0]):
        return False

    remaining = parts[1:]

    if remaining and _SCRIPT_RE.fullmatch(remaining[0]):
        remaining = remaining[1:]

    if remaining and _REGION_RE.fullmatch(remaining[0]):
        remaining = remaining[1:]

    return all(_VARIANT_RE.fullmatch(part) for part in remaining)


def _strip_locale_suffixes(language: str) -> str:
    return language.split(":", 1)[0].split(".", 1)[0].split("@", 1)[0]
