import numpy as np

from kiarina.agi.scd_model import SCDModel, SCDModelConfig


async def test_scd_model() -> None:
    scd_model = SCDModel(
        "example",
        SCDModelConfig(
            provider_name="mock",
            provider_config={
                "speaker_probabilities": [[0.1, 0.9]],
                "frame_ms": 100.0,
            },
        ),
    )

    print(f"__str__: {scd_model}")
    print(f"provider_name: {scd_model.provider_name}")
    print(f"provider_config: {scd_model.provider_config}")
    print(f"provider: {scd_model.provider}")

    result = await scd_model.predict(np.zeros(1600), 16000)

    assert result.frame_ms == 100.0
    assert np.allclose(result.speaker_probabilities, [[0.1, 0.9]])
