def normalize_time(time: float, duration: float) -> float:
    if time <= -1.0:
        normalized_time = duration + time + 1.0
    else:
        normalized_time = time

    return max(0.0, min(normalized_time, duration))
