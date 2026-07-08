from kiarina.agi.tts_provider_impl.command import (
    create_command_tts_provider,
)


def test_create_command_tts_provider() -> None:
    provider = create_command_tts_provider(
        command_args={"*": ["cp", "{input_file}", "{output_file}"]},
    )

    assert provider.settings.command_args == {
        "*": ["cp", "{input_file}", "{output_file}"]
    }
