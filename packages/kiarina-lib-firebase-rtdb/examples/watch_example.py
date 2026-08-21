"""
Example script to test watch_data functionality.

Usage:
    python examples/watch_example.py
"""

import asyncio

from kiarina.lib.firebase import FileTokenStore, TokenManager
from kiarina.lib.firebase_rtdb import watch_data


async def main() -> None:
    # TODO: Replace with your actual values
    api_key = "your_web_api_key_here"
    token_file_path = "~/.config/your-app/token.json"
    database_url = "https://your-project.firebaseio.com"
    watch_path = "/test"

    token_manager = TokenManager(
        api_key=api_key,
        token_store=FileTokenStore(token_file_path),
    )

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
