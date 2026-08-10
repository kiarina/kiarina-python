from typing import Literal


def format_time(seconds: float, format: Literal["srt", "webvtt"] = "srt") -> str:
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    ms = int((s % 1) * 1000)

    separator = "," if format == "srt" else "."
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{separator}{ms:03d}"
