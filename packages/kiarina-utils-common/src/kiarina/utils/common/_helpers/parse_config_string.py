from typing import Any

from .._types.config_str import ConfigStr


def parse_config_string(
    config_str: ConfigStr,
    *,
    separator: str = "&",
    key_value_separator: str = "=",
    nested_separator: str = ".",
    brackets: str = "()",
) -> dict[str, Any]:
    """
    Parse configuration string into nested dictionary

    When key contains nested_separator, it will be treated as nested keys:
    - hoge.fuga=30 → {"hoge": {"fuga": 30}}

    When key_value_separator is not found, the key is treated as a flag with None value:
    - debug&enabled=true → {"debug": None, "enabled": True}

    Values are automatically converted to appropriate types:
    - "true", "True" → bool(True)
    - "false", "False" → bool(False)
    - Numeric strings ("1", "0", "-5", etc.) → int/float
    - Others → str

    Bracketed values quote a substring so that separator / key_value_separator
    characters inside are not interpreted as delimiters. The default brackets
    are "(" and ")". A value that is fully wrapped by the brackets has the
    outer pair stripped and type-conversion suppressed (the inner text becomes
    a string verbatim). This is useful for embedding nested specifier strings.

    - key=(a&b=c) → {"key": "a&b=c"}
    - key=(123)   → {"key": "123"}   # not converted to int
    - key=()      → {"key": ""}

    Brackets must balance across the whole string; unbalanced brackets raise
    ValueError. Pass brackets="" to disable bracket handling entirely.

    Args:
        config_str: Configuration string to parse
        separator: Item separator (default: "&")
        key_value_separator: Key-value separator (default: "=")
        nested_separator: Nested key separator (default: ".")
        brackets: Two-character string giving the open and close bracket
            (default: "()"). Pass "" to disable bracket handling.

    Returns:
        Parsed configuration dictionary

    Examples:
        >>> parse_config_string("cache.enabled=true&db.port=5432")
        {"cache": {"enabled": True}, "db": {"port": 5432}}

        >>> parse_config_string("debug&verbose&cache.enabled=true")
        {"debug": None, "verbose": None, "cache": {"enabled": True}}

        >>> parse_config_string("key1:val1;key2.sub:42", separator=";", key_value_separator=":")
        {"key1": "val1", "key2": {"sub": 42}}

        >>> parse_config_string("vad=(mock?sample_rate=16000&p.0=1.0)&top_k=3")
        {"vad": "mock?sample_rate=16000&p.0=1.0", "top_k": 3}
    """
    if not config_str:
        return {}

    open_ch, close_ch = _validate_brackets(
        brackets, separator, key_value_separator, nested_separator
    )

    result: dict[str, Any] = {}

    for option in _split_top_level(config_str, separator, open_ch, close_ch):
        option = option.strip()

        if not option:
            continue

        key, raw_value = _split_kv(option, key_value_separator, open_ch, close_ch)

        if raw_value is None:
            # No key_value_separator found, treat as flag with None value
            _set_nested_value(result, key.strip(), None, nested_separator)
            continue

        key = key.strip()
        raw_value = raw_value.strip()

        value: Any
        if open_ch and _is_fully_wrapped(raw_value, open_ch, close_ch):
            # Strip outer brackets; keep inner content as a verbatim string
            # (no type conversion).
            value = raw_value[1:-1]
        else:
            value = _convert_value(raw_value)

        _set_nested_value(result, key, value, nested_separator)

    return result


def _validate_brackets(
    brackets: str,
    separator: str,
    key_value_separator: str,
    nested_separator: str,
) -> tuple[str, str]:
    """Validate brackets argument and return (open, close).

    Returns ("", "") when bracket handling is disabled.
    """
    if brackets == "":
        return "", ""

    if len(brackets) != 2:
        raise ValueError(f"brackets must be a 2-character string (got {brackets!r})")

    open_ch, close_ch = brackets[0], brackets[1]

    if open_ch == close_ch:
        raise ValueError(f"brackets open and close must differ (got {brackets!r})")

    for sep_name, sep in (
        ("separator", separator),
        ("key_value_separator", key_value_separator),
        ("nested_separator", nested_separator),
    ):
        if sep in (open_ch, close_ch):
            raise ValueError(f"brackets={brackets!r} conflicts with {sep_name}={sep!r}")

    return open_ch, close_ch


def _split_top_level(s: str, sep: str, open_ch: str, close_ch: str) -> list[str]:
    """Split s on sep at bracket depth 0.

    Tracks bracket depth so that occurrences of sep inside (...) are kept
    intact. Raises ValueError on unbalanced brackets.
    """
    if not open_ch:
        return s.split(sep)

    parts: list[str] = []
    buf: list[str] = []
    depth = 0

    for ch in s:
        if ch == open_ch:
            depth += 1
            buf.append(ch)
        elif ch == close_ch:
            depth -= 1
            if depth < 0:
                raise ValueError(f"Unbalanced {close_ch!r} in config string: {s!r}")
            buf.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)

    if depth != 0:
        raise ValueError(f"Unbalanced {open_ch!r} in config string: {s!r}")

    parts.append("".join(buf))
    return parts


def _split_kv(
    option: str, kv_sep: str, open_ch: str, close_ch: str
) -> tuple[str, str | None]:
    """Split option on the first key_value_separator at bracket depth 0.

    Returns (key, value) where value is None if kv_sep is not found at
    depth 0.
    """
    if not open_ch:
        if kv_sep in option:
            key, value = option.split(kv_sep, 1)
            return key, value
        return option, None

    depth = 0
    for i, ch in enumerate(option):
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
        elif ch == kv_sep and depth == 0:
            return option[:i], option[i + 1 :]

    return option, None


def _is_fully_wrapped(value: str, open_ch: str, close_ch: str) -> bool:
    """Return True if value is exactly one balanced (...) span.

    "(...)" → True, "(a)(b)" → False, "(a)x" → False, "" → False.
    """
    if len(value) < 2 or value[0] != open_ch or value[-1] != close_ch:
        return False

    depth = 0
    for i, ch in enumerate(value):
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0 and i != len(value) - 1:
                # Closed before the end → not a single wrap
                return False

    return depth == 0


def _convert_value(value: str) -> Any:
    """
    Convert string value to appropriate type

    Args:
        value: String value to convert

    Returns:
        Converted value
    """
    try:
        # Boolean values (only true and false, 1 and 0 are treated as numbers)
        if value.lower() == "true":
            return True

        elif value.lower() == "false":
            return False

        # Integer case
        elif value.lstrip("-").isdigit():
            return int(value)

        # Floating point case
        else:
            try:
                float_value = float(value)

                # Don't convert to integer if it can be represented as integer (respect original value)
                if "." in value:
                    return float_value
                else:
                    # If integer format but not caught above, treat as string
                    return value

            except ValueError:
                # String case
                return value

    except (ValueError, TypeError):
        # If conversion fails, save as string
        return value


def _set_nested_value(
    target: dict[str, Any], key: str, value: Any, separator: str = "."
) -> None:
    """
    Set value with nested keys (supports array indices)

    When a key is a numeric string, it's treated as an array index:
    - items.0:foo → {"items": ["foo"]}
    - users.0.name:Alice → {"users": [{"name": "Alice"}]}

    Args:
        target: Target dictionary to set the value
        key: Key (supports dot notation and array indices)
        value: Value to set
        separator: Nested key separator (default: ".")
    """
    keys = key.split(separator)

    current: dict[str, Any] | list[Any] = target

    # Navigate/create nested structure up to the last key
    for i, k in enumerate(keys[:-1]):
        next_key = keys[i + 1]

        if _is_array_index(k):
            index = int(k)

            if not isinstance(current, list):
                raise ValueError(
                    f"Cannot access array index {index} on non-array value"
                )

            while len(current) <= index:
                current.append(None)

            if _is_array_index(next_key):
                if current[index] is None:
                    current[index] = []
                elif not isinstance(current[index], list):
                    current[index] = []

            else:
                if current[index] is None:
                    current[index] = {}
                elif not isinstance(current[index], dict):
                    current[index] = {}

            current = current[index]

        else:
            if not isinstance(current, dict):
                raise ValueError(f"Cannot access key '{k}' on non-dict value")

            if _is_array_index(next_key):
                if k not in current:
                    current[k] = []
                elif not isinstance(current[k], list):
                    current[k] = []

                current = current[k]

            else:
                if k not in current:
                    current[k] = {}
                elif not isinstance(current[k], dict):
                    current[k] = {}

                current = current[k]

    # Set the value for the last key
    last_key = keys[-1]

    if _is_array_index(last_key):
        index = int(last_key)

        if not isinstance(current, list):
            raise ValueError(f"Cannot set array index {index} on non-array value")

        # Extend list if necessary (fill with None)
        while len(current) <= index:
            current.append(None)

        current[index] = value

    else:
        if not isinstance(current, dict):
            raise ValueError(f"Cannot set key '{last_key}' on non-dict value")

        current[last_key] = value


def _is_array_index(key: str) -> bool:
    """
    Check if a key represents an array index

    Args:
        key: Key to check

    Returns:
        True if key is a non-negative integer string
    """
    return key.isdigit()
