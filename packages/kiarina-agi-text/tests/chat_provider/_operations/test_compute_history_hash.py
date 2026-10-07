from kiarina.agi.chat_provider import compute_history_hash


def test_compute_history_hash() -> None:
    a = compute_history_hash([{"role": "user", "text": "名古屋", "n": 1}])

    assert a == compute_history_hash([{"n": 1, "text": "名古屋", "role": "user"}])
    assert a != compute_history_hash([{"role": "user", "text": "東京", "n": 1}])
    assert len(a) == 64
