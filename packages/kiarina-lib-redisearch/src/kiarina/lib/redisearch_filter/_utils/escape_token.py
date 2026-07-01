import re

ESCAPED_CHARACTERS: str = r"[,.<>{}\[\]\\\"\':;!@#$%^&*()\-+=~\/ ]"

ESCAPED_CHARACTERS_RE: re.Pattern[str] = re.compile(ESCAPED_CHARACTERS)


def escape_token(value: str) -> str:
    return ESCAPED_CHARACTERS_RE.sub(r"\\\g<0>", value)
