from dataclasses import dataclass


@dataclass
class AudioTagPrediction:
    label: str
    score: float
