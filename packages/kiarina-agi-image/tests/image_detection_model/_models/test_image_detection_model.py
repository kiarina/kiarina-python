# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

import numpy as np

from kiarina.agi.image_detection_model import (
    ImageDetectionModel,
    ImageDetectionModelConfig,
)


async def test_image_detection_model(run_context) -> None:
    image_detection_model = ImageDetectionModel(
        "example",
        ImageDetectionModelConfig(
            provider_name="mock",
            provider_config={
                "detections": [
                    {"bbox": [0.1, 0.1, 0.4, 0.4], "score": 0.8, "label": "cat"},
                ],
            },
        ),
    )

    print(f"__str__: {image_detection_model}")
    print(f"provider_name: {image_detection_model.provider_name}")
    print(f"provider_config: {image_detection_model.provider_config}")
    print(f"provider: {image_detection_model.provider}")

    result = await image_detection_model.detect(
        np.zeros((64, 64, 3), dtype=np.uint8), run_context=run_context
    )

    assert [d.label for d in result] == ["cat"]
    assert result[0].bbox == [0.1, 0.1, 0.4, 0.4]
