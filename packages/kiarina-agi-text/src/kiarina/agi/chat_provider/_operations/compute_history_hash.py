import hashlib
import json
from typing import Any


def compute_history_hash(history: Any) -> str:
    """
    A hash of a history in the form a provider sends it, such as its request
    items. JSON values are hashed in a canonical form.
    """
    text = json.dumps(
        history,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(text.encode()).hexdigest()
