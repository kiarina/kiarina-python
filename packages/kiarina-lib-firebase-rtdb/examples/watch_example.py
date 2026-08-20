"""
Example script to test watch_data functionality.

Usage:
    python examples/watch_example.py
"""

import asyncio

from kiarina.lib.firebase import TokenManager, refresh_id_token
from kiarina.lib.firebase_rtdb import watch_data


async def main() -> None:
    # TODO: Replace with your actual values
    api_key = "your_web_api_key_here"
    refresh_token = "your_refresh_token_here"
    database_url = "https://your-project.firebaseio.com"
    watch_path = "/test"

    token_data = await refresh_id_token(
        refresh_token=refresh_token,
        api_key=api_key,
    )
    token_manager = TokenManager(api_key=api_key, token_store=token_data)

    print(f"Starting to watch: {database_url}{watch_path}")
    print("Press Ctrl+C to stop\n")

    async for event in watch_data(
        database_url,
        watch_path,
        token_manager=token_manager,
    ):
        print("=" * 60)
        print(f"Event Type: {event.event_type}")
        print(f"Path: {event.path}")
        print(f"Data: {event.data}")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped watching")
