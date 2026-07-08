from kiarina.agi.asr_provider_impl.command import (
    CommandASRProvider,
    create_command_asr_provider,
)


def test_create_command_asr_provider() -> None:
    provider = create_command_asr_provider(
        text_command_args=["cp", "{input_file}", "{output_file}"],
        text_output_file_suffix=".txt",
    )

    assert isinstance(provider, CommandASRProvider)
    assert provider.settings.text_command_args == [
        "cp",
        "{input_file}",
        "{output_file}",
    ]
    assert provider.settings.text_output_file_suffix == ".txt"
