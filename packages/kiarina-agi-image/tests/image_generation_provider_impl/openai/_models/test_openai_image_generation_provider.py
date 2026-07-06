# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import pytest

from kiarina.agi.image_generation_provider_impl.openai import (
    OpenAIImageGenerationProvider,
    OpenAIImageGenerationProviderSettings,
)


def test_init_and_properties() -> None:
    settings = OpenAIImageGenerationProviderSettings()
    provider = OpenAIImageGenerationProvider(settings)

    print(str(provider))
    print(f"openai_settings: {provider.openai_settings}")


@pytest.mark.costly
async def test_generate_without_and_with_images(
    cost_recorder, run_context, tmp_path
) -> None:
    settings = OpenAIImageGenerationProviderSettings()
    provider = OpenAIImageGenerationProvider(settings)

    result = await provider.generate(
        prompt="A cute cat sitting on a sofa, digital art",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    file_path = tmp_path / result.mime_blob.hashed_file_name
    file_path.write_bytes(result.mime_blob.raw_data)

    print("---- Create Image ----")
    print(f"Image saved to: '{file_path}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    cost_recorder.clear()

    result = await provider.generate(
        prompt="Add a hat to the cat",
        file_paths=[str(file_path)],
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    edited_file_path = tmp_path / f"edited_{result.mime_blob.hashed_file_name}"
    edited_file_path.write_bytes(result.mime_blob.raw_data)

    print("---- Edit Image ----")
    print(f"Edited image saved to: '{edited_file_path}'")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")
