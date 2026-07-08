import re

from .._schemas.asr_segment import ASRSegment

_TIMESTAMP_PATTERN = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
    r"(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})"
)


def parse_srt(text: str) -> list[ASRSegment]:
    segments: list[ASRSegment] = []

    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]

        if not lines:
            continue

        if lines[0].isdigit():
            lines = lines[1:]

        if not lines:
            continue

        match = _TIMESTAMP_PATTERN.search(lines[0])

        if not match:
            continue

        body = "\n".join(lines[1:]).strip()
        metadata: dict[str, str] = {}

        speaker_match = re.match(r"^\[(?P<speaker>[^\]]+)\]\s*(?P<text>.*)$", body)
        if speaker_match:
            metadata["speaker_name"] = speaker_match.group("speaker")
            body = speaker_match.group("text")

        segments.append(
            ASRSegment(
                text=body,
                start_timestamp=_parse_timestamp(match.group("start")),
                end_timestamp=_parse_timestamp(match.group("end")),
                metadata=metadata,
            )
        )

    return segments


def _parse_timestamp(value: str) -> float:
    hms, milliseconds = re.split(r"[,.]", value, maxsplit=1)
    hours, minutes, seconds = [int(part) for part in hms.split(":")]
    return hours * 3600 + minutes * 60 + seconds + int(milliseconds) / 1000
