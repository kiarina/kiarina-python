import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any, Literal, cast

import httpx

from kiarina.lib.firebase import TokenManager

from .._exceptions.rtdb_stream_cancelled_error import RTDBStreamCancelledError
from .._schemas.data_change_event import DataChangeEvent
from .._settings import settings_manager

logger = logging.getLogger(__name__)


async def watch_data(
    database_url: str,
    path: str,
    token_manager: TokenManager,
    *,
    stop_event: asyncio.Event | None = None,
) -> AsyncIterator[DataChangeEvent]:
    logger.debug(f"Starting watch on {path} in {database_url}")
    settings = settings_manager.get_settings()
    retry_delay = settings.initial_retry_delay

    while True:
        if stop_event and stop_event.is_set():
            logger.debug("Stop event set, exiting watch loop")
            break

        try:
            async for event in _watch_stream(
                database_url, path, token_manager, stop_event
            ):
                yield event
                retry_delay = settings.initial_retry_delay

            # Firebase normally keeps the stream open until the caller stops it.
            logger.info("Stream ended normally, exiting watch loop")
            break

        except _AuthRevokedError:
            logger.info("Auth revoked, refreshing token and reconnecting")
            await token_manager.refresh()
            retry_delay = settings.initial_retry_delay
            continue

        except (httpx.HTTPError, httpx.StreamError) as e:
            logger.warning(
                f"Network error during watch: {e}, retrying in {retry_delay}s"
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(
                retry_delay * settings.retry_delay_multiplier, settings.max_retry_delay
            )
            continue

        except Exception as e:
            logger.error(f"Unexpected error during watch: {e}")
            raise


async def _watch_stream(
    database_url: str,
    path: str,
    token_manager: TokenManager,
    stop_event: asyncio.Event | None = None,
) -> AsyncIterator[DataChangeEvent]:
    id_token = await token_manager.get_id_token()

    url = f"{database_url.rstrip('/')}{path}.json"
    params = {"auth": id_token}
    headers = {"Accept": "text/event-stream"}

    async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
        async with client.stream(
            "GET", url, params=params, headers=headers
        ) as response:
            response.raise_for_status()

            async for event in _parse_sse_stream(response, stop_event):
                yield event


async def _parse_sse_stream(
    response: httpx.Response,
    stop_event: asyncio.Event | None = None,
) -> AsyncIterator[DataChangeEvent]:
    buffer = ""

    async for chunk in response.aiter_text():
        if stop_event and stop_event.is_set():
            logger.debug("Stop event set during stream parsing")
            return

        buffer += chunk
        lines = buffer.split("\n")

        buffer = lines[-1]
        lines = lines[:-1]

        event_type: str | None = None
        event_data: str | None = None

        for line in lines:
            line = line.strip()

            if not line:
                # An empty line terminates an SSE event.
                if event_type is not None:
                    event = _handle_sse_event(event_type, event_data)

                    if event is not None:
                        yield event

                    event_type = None
                    event_data = None

                continue

            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                event_data = line[5:].strip()


def _handle_sse_event(
    event_type: str,
    event_data: str | None,
) -> DataChangeEvent | None:
    if event_type == "keep-alive":
        return None

    elif event_type == "cancel":  # pragma: no cover
        raise RTDBStreamCancelledError(f"Stream cancelled: {event_data}")

    elif event_type == "auth_revoked":  # pragma: no cover
        raise _AuthRevokedError()

    elif event_type in ("put", "patch"):
        parsed_data = _parse_event_data(event_data)
        event_path = parsed_data.get("path", "")
        data = parsed_data.get("data")

        return DataChangeEvent(
            event_type=cast(Literal["put", "patch"], event_type),
            path=event_path,
            data=data,
        )

    else:  # pragma: no cover
        logger.warning(f"Unknown event type: {event_type}, data: {event_data}")
        return None


def _parse_event_data(event_data: str | None) -> dict[str, Any]:
    if not event_data:
        return {}

    try:
        parsed = json.loads(event_data)

        if not isinstance(parsed, dict):
            logger.warning(
                f"Event data is not a dict: {type(parsed)}, data: {event_data}"
            )
            return {}

        return parsed

    except json.JSONDecodeError as e:  # pragma: no cover
        logger.warning(f"Failed to parse event data: {e}, data: {event_data}")
        return {}


class _AuthRevokedError(Exception):
    pass
