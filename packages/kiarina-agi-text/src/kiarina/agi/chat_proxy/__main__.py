from kiarina.utils.app import configure

from ._helpers.run_chat_proxy import run_chat_proxy


def main() -> None:
    # The asset repository stores the sent files under the app's directories.
    configure(app_author="kiarina", app_name="kiarina-chat-proxy")
    run_chat_proxy()


if __name__ == "__main__":
    main()
