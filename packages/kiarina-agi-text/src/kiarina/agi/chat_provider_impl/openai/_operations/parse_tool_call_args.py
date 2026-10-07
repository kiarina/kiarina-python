import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_tool_call_args(arguments: str | None) -> dict[str, Any]:
    if not arguments:
        return {}

    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        logger.warning("Failed to parse tool call arguments: %s", arguments)
        return {}

    if not isinstance(args, dict):
        logger.warning("Tool call arguments are not an object: %s", arguments)
        return {}

    return args
