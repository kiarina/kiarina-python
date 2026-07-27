import re
from datetime import datetime

# Firestore returns RFC 3339 timestamps with up to nanosecond precision,
# while datetime.fromisoformat() accepts at most microseconds.
_EXCESS_FRACTION = re.compile(r"\.(\d{6})\d+")


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(_EXCESS_FRACTION.sub(r".\1", value))
