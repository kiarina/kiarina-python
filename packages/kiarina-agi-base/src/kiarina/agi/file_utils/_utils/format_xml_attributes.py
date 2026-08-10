from typing import Any


def format_xml_attributes(xml_attributes: dict[str, Any]) -> str:
    parts: list[str] = []

    for key, value in xml_attributes.items():
        if value is None:  # pragma: no cover
            continue

        parts.append(f' {key}="{value}"')

    return "".join(parts)
