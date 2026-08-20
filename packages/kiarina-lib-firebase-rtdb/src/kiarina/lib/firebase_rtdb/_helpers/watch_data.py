import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any, Literal, cast

import httpx

from kiarina.lib.firebase import (
    FirebaseAPIError,
    InvalidRefreshTokenError,
    TokenManager,
)

from .._exceptions.rtdb_stream_cancelled_error import RTDBStreamCancelledError
from .._operations.resolve_token_manager import resolve_token_manager
from .._schemas.data_change_event import DataChangeEvent
from .._settings import settings_manager

logger = logging.getLogger(__name__)


async def watch_data(
    database_url: str,
    path: str,
    *,
    stop_event: asyncio.Event | None = None,
    token_manager: TokenManager | None = None,
) -> AsyncIterator[DataChangeEvent]:
    logger.debug(f"Starting watch on {path} in {database_url}")
    token_manager = resolve_token_manager(token_manager)

    settings = settings_manager.get_settings()
    retry_delay = settings.initial_retry_delay
    refresh_pending = False

    while True:
        if stop_event and stop_event.is_set():
            logger.debug("Stop event set, exiting watch loop")
            break

        received_event = False

        try:
            if refresh_pending:
                await token_manager.refresh()
                refresh_pending = False

            async for event in _watch_stream(
                database_url, path, token_manager, stop_event
            ):
                received_event = True
                retry_delay = settings.initial_retry_delay
                yield event

            # Firebase normally keeps the stream open until the caller stops it.
            logger.info("Stream ended normally, exiting watch loop")
            break

        except _AuthRevokedError:
            refresh_pending = True

            # A revocation after a healthy stream is the expected token rotation.
            if received_event:
                logger.info("Auth revoked, refreshing token and reconnecting")
                continue

            logger.warning(f"Auth revoked before any event, retrying in {retry_delay}s")

        except InvalidRefreshTokenError as e:
            logger.error(f"Refresh token is no longer usable: {e}")
            raise

        except FirebaseAPIError as e:
            if not _is_retryable_api_error(e):
                logger.error(f"Token refresh failed: {e}")
                raise

            logger.warning(f"Token refresh failed: {e}, retrying in {retry_delay}s")

        except (httpx.HTTPError, httpx.StreamError) as e:
            logger.warning(
                f"Network error during watch: {e}, retrying in {retry_delay}s"
            )

        except Exception as e:
            logger.error(f"Unexpected error during watch: {e}")
            raise

        await asyncio.sleep(retry_delay)
        retry_delay = min(
            retry_delay * settings.retry_delay_multiplier, settings.max_retry_delay
        )


def _is_retryable_api_error(error: FirebaseAPIError) -> bool:
    if error.status_code is None:
        # Raised from a transport failure rather than an API response.
        return True

    return error.status_code == 429 or error.status_code >= 500


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
