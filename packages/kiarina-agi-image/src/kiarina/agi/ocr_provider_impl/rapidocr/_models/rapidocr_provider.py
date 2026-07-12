from typing import Any

import numpy as np

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.image_types import ImagePixels
from kiarina.agi.ocr_provider import BaseOCRProvider, OCRResult
from kiarina.agi.run_context import RunContext

from .._settings import RapidOCRProviderSettings

try:
    from rapidocr import (  # type: ignore[import-not-found]
        EngineType,
        LangDet,
        LangRec,
        ModelType,
        OCRVersion,
        RapidOCR,
    )
except ImportError as exc:
    raise ImportError(
        "rapidocr and onnxruntime are required to use RapidOCRProvider. "
        "Install them with: pip install 'kiarina-agi-image[ocr-provider-rapidocr]'"
    ) from exc


class RapidOCRProvider(BaseOCRProvider):
    def __init__(self, settings: RapidOCRProviderSettings) -> None:
        super().__init__()
        self.settings = settings
        self._engine: Any | None = None

    @property
    def engine(self) -> Any:
        if self._engine is None:
            self._engine = RapidOCR(
                params={
                    "Det.engine_type": EngineType.ONNXRUNTIME,
                    "Det.lang_type": LangDet.CH,
                    "Det.model_type": ModelType.SMALL,
                    "Det.ocr_version": OCRVersion.PPOCRV6,
                    "Rec.engine_type": EngineType.ONNXRUNTIME,
                    "Rec.lang_type": LangRec.JAPAN,
                    "Rec.model_type": ModelType.SMALL,
                    "Rec.ocr_version": OCRVersion.PPOCRV6,
                }
            )
        return self._engine

    def _ocr(
        self,
        pixels: ImagePixels,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[OCRResult]:
        height, width = pixels.shape[:2]
        output = self.engine(
            self._to_bgr(pixels),
            text_score=self.settings.text_score,
            box_thresh=self.settings.box_threshold,
            unclip_ratio=1.6,
        )
        if output.boxes is None or output.txts is None or output.scores is None:
            return []
        return [
            OCRResult(
                text=text,
                score=float(score),
                polygon=[
                    [float(point[0]) / width, float(point[1]) / height]
                    for point in np.asarray(box)
                ],
            )
            for box, text, score in zip(
                output.boxes, output.txts, output.scores, strict=True
            )
        ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(PP-OCRv6-small)"
