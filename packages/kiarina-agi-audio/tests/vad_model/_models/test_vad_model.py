import numpy as np

from kiarina.agi.vad_model import VADModel, VADModelConfig


async def test_vad_model() -> None:
    vad_model = VADModel(
        "example",
        VADModelConfig(
            provider_name="mock",
            provider_config={
                "speech_probabilities": [0.0],
            },
        ),
    )

    print(f"__str__: {vad_model}")
    print(f"provider_name: {vad_model.provider_name}")
    print(f"provider_config: {vad_model.provider_config}")
    print(f"provider: {vad_model.provider}")

    assert await vad_model.predict(np.zeros(512), 16000) == 0.0
