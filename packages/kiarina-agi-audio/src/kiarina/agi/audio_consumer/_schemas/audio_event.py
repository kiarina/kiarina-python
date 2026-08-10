from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .._types.audio_consumer_name import AudioConsumerName


@dataclass(kw_only=True)
class AudioEvent:
    consumer_name: AudioConsumerName
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
