import math
from typing import Literal


def calc_score(
    distance: float,
    *,
    datatype: Literal["FLOAT32", "FLOAT64"],
    distance_metric: Literal["COSINE", "IP", "L2"],
) -> float:
    if datatype == "FLOAT32":
        distance = round(distance, 4)
    else:
        distance = round(distance, 7)

    if distance_metric == "COSINE":
        return 1.0 - distance

    elif distance_metric == "IP":
        if distance > 0:
            return 1.0 - distance
        else:
            return -1.0 * distance

    elif distance_metric == "L2":
        return 1.0 - distance / math.sqrt(2)

    else:
        raise ValueError(f"Unsupported distance metric: {distance_metric}")
