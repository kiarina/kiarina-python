from kiarina.agi.chat_provider_impl.claude_code._operations.create_child_env import (
    create_child_env,
)


def test_create_child_env() -> None:
    env = create_child_env(
        {
            "ANTHROPIC_API_KEY": "sk-live",
            "ANTHROPIC_BASE_URL": "https://proxy",
            "CLAUDE_CODE_OAUTH_TOKEN": "host",
            "CLAUDE_CODE_ENTRYPOINT": "cli",
            "HOME": "/home/me",
        },
        {"ANTHROPIC_BASE_URL": "http://127.0.0.1:9"},
    )

    assert env == {
        "ANTHROPIC_API_KEY": "",
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:9",
        "CLAUDE_CODE_OAUTH_TOKEN": "",
    }
