from dataclasses import dataclass


@dataclass
class OCRResult:
    text: str
    score: float
    polygon: list[list[float]]
