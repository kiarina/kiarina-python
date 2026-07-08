import numpy as np
import pytest

from kiarina.agi.scd_provider_impl.pyannote import (
    PyannoteSCDProvider,
    PyannoteSCDProviderSettings,
)


def test_pyannote_scd_provider_powerset_mapping() -> None:
    provider = PyannoteSCDProvider(PyannoteSCDProviderSettings(model_path="dummy.onnx"))

    assert provider.powerset_mapping.tolist() == [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 1.0],
    ]


def test_pyannote_scd_provider_converts_powerset_log_probs() -> None:
    provider = PyannoteSCDProvider(
        PyannoteSCDProviderSettings(
            model_path="dummy.onnx",
            output_kind="powerset_log_probs",
        )
    )
    powerset_probs = np.array(
        [
            [0.1, 0.8, 0.1, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.7, 0.2, 0.1],
        ],
        dtype=np.float32,
    )

    with np.errstate(divide="ignore"):
        speaker_probs = provider._to_speaker_probabilities(np.log(powerset_probs))

    assert np.allclose(
        speaker_probs,
        np.array(
            [
                [0.8, 0.1, 0.0],
                [0.9, 0.8, 0.3],
            ],
            dtype=np.float32,
        ),
    )


@pytest.mark.downloads_model
async def test_pyannote_scd_provider() -> None:
    provider = PyannoteSCDProvider(PyannoteSCDProviderSettings())

    result = await provider.predict(np.zeros(16000, dtype=np.float32), 16000)

    assert result.frame_ms > 0.0
    assert result.speaker_probabilities.ndim == 2
    assert result.speaker_probabilities.shape[1] == 3
